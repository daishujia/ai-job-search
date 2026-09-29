"""Post-download verification, PROVENANCE.md, files.tsv and the omics CATALOG.tsv.

Fast mode (inline): presence, no leftover .aria2 control file, exact sizes.
Deep mode (detached background process): also re-hashes every file that has a checksum.
    python -m nas_mcp.verify --config CONFIG JOB_ID
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from . import NasError
from .config import Config, load_config
from .jobs import _dir_size, load_job
from .manifest import Plan, human
from .paths import safe_relpath

HASHERS = {"md5": hashlib.md5, "sha-1": hashlib.sha1, "sha-256": hashlib.sha256}


def _hash(path: Path, algo: str) -> str:
    h = HASHERS[algo]()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_files(cfg: Config, job: dict, deep: bool) -> dict:
    dest = Path(job["dest"])
    plan = Plan.load(cfg, job["plan_id"])
    rows, counts = [], {}
    for f in plan.files:
        p = dest / safe_relpath(f.relpath)
        if Path(str(p) + ".aria2").exists():
            st = "partial"
        elif not p.is_file():
            st = "missing"
        elif f.size_exact and f.size is not None and p.stat().st_size != f.size:
            st = "size_mismatch"
        elif deep and f.checksum and f.checksum_type in HASHERS:
            match = _hash(p, f.checksum_type) == f.checksum.lower()
            st = "hash_ok" if match else ("etag_differs" if f.attrs.get("advisory_checksum") else "hash_mismatch")
        else:
            st = "ok"
        counts[st] = counts.get(st, 0) + 1
        rows.append((f, p, st))
    # etag_differs is informational: S3 ETags are not MD5s for SSE-KMS objects; size already matched.
    bad = [{"path": f.relpath, "status": st} for f, _, st in rows if st not in ("ok", "hash_ok", "etag_differs")]
    return {"counts": counts, "problems": bad, "rows": rows, "plan": plan}


def write_provenance(cfg: Config, job: dict, plan: Plan, rows: list, summary: dict) -> None:
    dest = Path(job["dest"])
    with open(dest / "files.tsv", "w") as fh:
        fh.write("relpath\tbytes\tchecksum_type\tchecksum\tverification\tsource_url\n")
        for f, p, st in rows:
            size = p.stat().st_size if p.is_file() else ""
            fh.write(f"{f.relpath}\t{size}\t{f.checksum_type or ''}\t{f.checksum or ''}\t{st}\t"
                     f"{f.url.split('?')[0]}\n")  # strip signed-URL query strings
    m = plan.meta
    params = {k: v for k, v in plan.params.items() if "token" not in k.lower()}
    total = sum(p.stat().st_size for _, p, _ in rows if p.is_file()) if rows else _dir_size(dest)
    lines = [
        f"# {m.get('title') or plan.dataset_id}", "",
        f"- **Registry id:** `{plan.dataset_id}`  |  **Connector:** `{plan.connector}`",
        f"- **Accession / source:** {m.get('accession', '')} {m.get('source_url', '')}",
        f"- **Version / revision:** {m.get('version') or m.get('revision') or 'n/a'}",
        f"- **Licence / terms:** {m.get('license') or 'see source'}",
        f"- **Access policy:** {plan.policy}" + (f" — acknowledgement: {job['policy_ack']}" if job.get("policy_ack") else ""),
        f"- **Downloaded:** {time.strftime('%Y-%m-%d', time.localtime(job['created']))} "
        f"→ verified {time.strftime('%Y-%m-%d %H:%M')} (job `{job['job_id']}`)",
        f"- **Files / size:** {len(rows) or 'see folder'} files, {human(total)}",
        f"- **Verification:** {summary.get('counts')} ({'deep checksum' if summary.get('deep') else 'size/presence'})",
        f"- **Plan parameters:** `{json.dumps(params)}`",
    ]
    if m.get("citation") or m.get("doi"):
        lines.append(f"- **Cite:** {m.get('citation') or ''} {m.get('doi') or ''}".rstrip())
    if m.get("notes"):
        lines.append(f"- **Notes:** {m['notes']}")
    lines += ["", "Per-file checksums and source URLs: `files.tsv`.", ""]
    (dest / "PROVENANCE.md").write_text("\n".join(lines))

    catalog = cfg.omics_root / "CATALOG.tsv"
    header = "date\tdataset_id\taccession\ttitle\tpath\tfiles\tbytes\tpolicy\tjob_id\n"
    existing = catalog.read_text() if catalog.exists() else header
    keep = [l for l in existing.splitlines(keepends=True) if not l.rstrip("\n").endswith("\t" + job["job_id"])]
    if not keep or not keep[0].startswith("date\t"):
        keep.insert(0, header)
    keep.append(f"{time.strftime('%Y-%m-%d')}\t{plan.dataset_id}\t{m.get('accession', '')}\t"
                f"{(m.get('title') or '').replace(chr(9), ' ')[:120]}\t{dest}\t{len(rows)}\t{total}\t"
                f"{plan.policy}\t{job['job_id']}\n")
    catalog.write_text("".join(keep))


def run(cfg: Config, job_id: str, deep: bool = False) -> dict:
    job = load_job(cfg, job_id)
    if job["kind"] == "process":
        rc = Path(job["exitfile"]).read_text().strip() if Path(job["exitfile"]).exists() else None
        if rc != "0":
            raise NasError(f"Job {job_id} has not finished successfully (exit={rc}); see nas_job_status log.")
        plan = Plan.load(cfg, job["plan_id"])
        summary = {"counts": {"process_exit_0": 1}, "deep": False}
        write_provenance(cfg, job, plan, [], summary)
        return {"job_id": job_id, "result": "ok", **summary, "provenance": str(Path(job["dest"]) / "PROVENANCE.md")}
    res = check_files(cfg, job, deep)
    summary = {"counts": res["counts"], "deep": deep}
    ok = not res["problems"]
    if ok:
        write_provenance(cfg, job, res["plan"], res["rows"], summary)
    return {"job_id": job_id, "result": "ok" if ok else "problems", **summary,
            "problems": res["problems"][:25],
            "provenance": str(Path(job["dest"]) / "PROVENANCE.md") if ok else None}


def start_deep(cfg: Config, job_id: str, restart: bool = False) -> dict:
    load_job(cfg, job_id)
    out = cfg.jobs_dir / f"{job_id}.verify.json"
    if restart:
        out.unlink(missing_ok=True)
    running = cfg.jobs_dir / f"{job_id}.verify.pid"
    if running.exists():
        try:
            os.kill(int(running.read_text()), 0)
            return {"job_id": job_id, "deep_verify": "running", "hint": "Call again later for the result."}
        except (ProcessLookupError, ValueError):
            running.unlink(missing_ok=True)
    if out.exists():
        return {"job_id": job_id, "deep_verify": "finished", **json.loads(out.read_text()),
                "hint": "To re-run, pass restart=true."}
    log = cfg.logs_dir / f"{job_id}.verify.log"
    with open(log, "ab") as fh:
        p = subprocess.Popen([sys.executable, "-m", "nas_mcp.verify", "--config", str(cfg.source_path), job_id],
                             stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, start_new_session=True)
    running.write_text(str(p.pid))
    return {"job_id": job_id, "deep_verify": "started", "pid": p.pid}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    ap.add_argument("job_id")
    a = ap.parse_args()
    cfg = load_config(a.config)
    try:
        result = run(cfg, a.job_id, deep=True)
    except NasError as e:
        result = {"result": "error", "error": str(e)}
    (cfg.jobs_dir / f"{a.job_id}.verify.json").write_text(json.dumps(result))
    (cfg.jobs_dir / f"{a.job_id}.verify.pid").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
