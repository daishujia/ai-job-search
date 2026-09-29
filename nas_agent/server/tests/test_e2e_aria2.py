"""End-to-end against a real aria2c daemon and a local HTTP server (no internet needed)."""
import functools
import hashlib
import json
import http.server
import os
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest

from nas_mcp import NasError, jobs, verify
from nas_mcp.manifest import FileEntry, Plan, new_plan_id
from nas_mcp.planning import plan_urls

pytestmark = pytest.mark.e2e
if not shutil.which("aria2c"):
    pytest.skip("aria2c not installed", allow_module_level=True)


def _port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class _Quiet(http.server.SimpleHTTPRequestHandler):
    """Static server with single-range support (like S3/PRIDE), so resume can be tested."""

    def log_message(self, *a):
        pass

    def do_GET(self):
        rng = self.headers.get("Range")
        path = Path(self.translate_path(self.path))
        if not rng or not path.is_file():
            return super().do_GET()
        size = path.stat().st_size
        start, _, end = rng.removeprefix("bytes=").partition("-")
        start, end = int(start), int(end) if end else size - 1
        self.send_response(206)
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        with open(path, "rb") as fh:
            fh.seek(start)
            left = end - start + 1
            try:
                while left > 0:
                    chunk = fh.read(min(left, 1 << 16))
                    self.wfile.write(chunk)
                    left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass


@pytest.fixture
def served(tmp_path):
    root = tmp_path / "www"
    (root / "sub").mkdir(parents=True)
    (root / "a.tsv").write_bytes(b"protein\tvalue\nAPP\t1.0\n" * 1000)
    (root / "sub" / "b.bin").write_bytes(os.urandom(300_000))
    with open(root / "big.bin", "wb") as fh:  # 64 MB, served slowly via aria2 speed limit
        fh.truncate(64 * 1024 * 1024)
    port = _port()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(_Quiet, directory=str(root)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield root, f"http://127.0.0.1:{port}"
    srv.shutdown()


@pytest.fixture
def aria2(cfg, tmp_path):
    port, secret = _port(), "s3cr3t-test"
    sf = tmp_path / "aria2.secret"
    sf.write_text(secret)
    env = {k: v for k, v in os.environ.items() if "proxy" not in k.lower()}
    p = subprocess.Popen(["aria2c", "--enable-rpc", f"--rpc-listen-port={port}", "--rpc-listen-all=false",
                          f"--rpc-secret={secret}", "--max-overall-download-limit=2M", "--max-download-result=100000",
                          "--console-log-level=warn", "--quiet=true"], env=env)
    cfg.aria2_url, cfg.aria2_secret_file = f"http://127.0.0.1:{port}/jsonrpc", sf
    for _ in range(50):
        try:
            jobs.aria2_client(cfg).version()
            break
        except NasError:
            time.sleep(0.1)
    yield cfg
    p.terminate()
    p.wait()


def _wait(cfg, job_id, states=("complete", "error"), timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = jobs.status(cfg, job_id)
        if st["state"] in states:
            return st
        time.sleep(0.3)
    raise AssertionError(f"timeout; last={st}")


def test_download_verify_provenance_and_resubmit(aria2, served):
    cfg, (root, base) = aria2, served
    md5 = hashlib.md5((root / "a.tsv").read_bytes()).hexdigest()
    sha = hashlib.sha256((root / "sub/b.bin").read_bytes()).hexdigest()
    plan = plan_urls(cfg, [{"url": f"{base}/a.tsv", "md5": md5},
                           {"url": f"{base}/sub/b.bin", "sha256": sha, "name": "b.bin"}], "E2E", "ds1")
    out = jobs.submit(cfg, plan)
    assert out["queued"] == 2
    st = _wait(cfg, out["job_id"])
    assert st["state"] == "complete", st
    dest = Path(plan.dest)
    assert dest == cfg.omics_root.resolve() / "E2E" / "ds1"
    assert (dest / "processed" / "a.tsv").read_bytes() == (root / "a.tsv").read_bytes()

    v = verify.run(cfg, out["job_id"])
    assert v["result"] == "ok" and v["counts"] == {"ok": 2}
    prov = (dest / "PROVENANCE.md").read_text()
    assert "open-urls" in prov and "allowed" in prov and "/Volumes/AI4Sci/database/E2E/ds1" in prov
    assert "processed/a.tsv\t" in (dest / "files.tsv").read_text()
    assert out["job_id"] in (cfg.catalog_dir / "downloads.tsv").read_text()
    # verification drafted standard metadata and indexed it
    assert v["metadata_draft"] == "metadata/study.draft.json" and (dest / "metadata/source/_plan.json").exists()
    assert "E2E\tds1" in (cfg.omics_root / "CATALOG.tsv").read_text()

    # deep verify runs detached and re-hashes
    assert verify.start_deep(cfg, out["job_id"])["deep_verify"] == "started"
    for _ in range(100):
        r = verify.start_deep(cfg, out["job_id"])
        if r["deep_verify"] == "finished":
            break
        time.sleep(0.2)
    assert r["counts"] == {"hash_ok": 2}, r

    again = jobs.submit(cfg, Plan.load(cfg, plan.plan_id))
    assert again["queued"] == 0 and again["skipped_existing"] == 2
    # verifying twice must not duplicate the catalog row
    verify.run(cfg, out["job_id"])
    assert (cfg.catalog_dir / "downloads.tsv").read_text().count(out["job_id"]) == 1


def test_checksum_mismatch_is_an_error(aria2, served):
    cfg, (_, base) = aria2, served
    plan = plan_urls(cfg, [{"url": f"{base}/a.tsv", "md5": "0" * 32}], "E2E", "bad")
    st = _wait(cfg, jobs.submit(cfg, plan)["job_id"])
    assert st["state"] == "error" and st["errors"] and st["hint"]
    assert verify.run(cfg, plan.plan_id)["result"] == "problems"


def test_space_and_size_guards(aria2, served, monkeypatch):
    cfg, (_, base) = aria2, served
    big = plan_urls(cfg, [{"url": f"{base}/big.bin", "size": 2 * 1024**3}], "E2E", "guard")
    with pytest.raises(NasError, match="confirm_large"):
        jobs.submit(cfg, big)
    monkeypatch.setattr(jobs, "free_bytes", lambda p: (10 * 1024**2, 100 * 1024**3))
    with pytest.raises(NasError, match="Not enough space"):
        jobs.submit(cfg, big, confirm_large=True)


def test_pause_resume_cancel_purge(aria2, served):
    cfg, (_, base) = aria2, served
    plan = plan_urls(cfg, [f"{base}/big.bin"], "E2E", "slow")
    job_id = jobs.submit(cfg, plan)["job_id"]
    _wait(cfg, job_id, states=("running",))
    time.sleep(1)
    assert jobs.control(cfg, job_id, "pause")["applied"] == 1
    assert _wait(cfg, job_id, states=("paused",))["state"] == "paused"
    assert jobs.control(cfg, job_id, "resume")["applied"] == 1
    _wait(cfg, job_id, states=("running",))
    r = jobs.control(cfg, job_id, "cancel", purge_partial=True)
    assert r["applied"] == 1
    time.sleep(0.5)
    assert not (Path(plan.dest) / "processed" / "big.bin").exists()


def test_process_job_detached(cfg):
    dest = cfg.omics_root / "AMP-AD" / "syn1"
    plan = Plan(plan_id=new_plan_id(), dataset_id="amp-ad", connector="synapse", params={"syn_id": "syn1"},
                dest=str(dest), policy="check_dua", kind="process", source="AMP-AD", project_code="syn1",
                command=["sh", "-c", "sleep 0.5; mkdir -p {dest}/_incoming/sub; echo data > {dest}/_incoming/sub/x.tsv; "
                                     "echo s > {dest}/_incoming/README.md"], meta={"title": "fake synapse"})
    plan.save(cfg)
    with pytest.raises(NasError, match="policy_ack"):
        jobs.submit(cfg, plan)
    job_id = jobs.submit(cfg, plan, policy_ack="AMP-AD DUC (personal approval), test")["job_id"]
    assert jobs.status(cfg, job_id)["state"] == "running"
    st = _wait(cfg, job_id, states=("complete", "error", "stopped"), timeout=20)
    assert st["state"] == "complete"
    v = verify.run(cfg, job_id)
    assert v["result"] == "ok" and v["counts"]["organised_files"] == 2
    assert (dest / "processed/sub/x.tsv").read_text() == "data\n" and (dest / "metadata/README.md").exists()
    assert not (dest / "_incoming").exists()
    assert "personal approval" in (dest / "PROVENANCE.md").read_text()
    draft = json.loads((dest / "metadata/study.draft.json").read_text())
    assert draft["identity"]["dua_reference"].startswith("AMP-AD DUC") and draft["identity"]["access_policy"] == "check_dua"


def test_s3_style_advisory_etag_is_not_enforced(aria2, served):
    """A wrong advisory (S3 ETag) checksum must not fail the download, and deep verify only notes it."""
    cfg, (_, base) = aria2, served
    plan = plan_urls(cfg, [f"{base}/a.tsv"], "E2E", "etag")
    plan.files[0].checksum_type, plan.files[0].checksum = "md5", "0" * 32
    plan.files[0].attrs = {"advisory_checksum": True}
    plan.save(cfg)
    st = _wait(cfg, jobs.submit(cfg, plan)["job_id"])
    assert st["state"] == "complete", st
    res = verify.check_files(cfg, jobs.load_job(cfg, plan.plan_id), deep=True)
    assert res["counts"] == {"etag_differs": 1} and res["problems"] == []
