"""Live checks against the real public APIs (network). Run: pytest -m live
Downloads are tiny (<1 MB each) and go through a real aria2c when available."""
import os
import shutil
import subprocess
import time

import pytest

from nas_mcp import jobs, verify
from nas_mcp.http import Http
from nas_mcp.planning import browse, plan_dataset

pytestmark = pytest.mark.live
if os.environ.get("NAS_MCP_LIVE") != "1":
    pytest.skip("set NAS_MCP_LIVE=1 to run live API tests", allow_module_level=True)


@pytest.fixture(scope="module")
def http():
    return Http()


def test_pride_listing(cfg, http):
    p = plan_dataset(cfg, "pride", {"accession": "PXD000001"}, None, None, None, None, http)
    assert p.files and all(f.url.startswith("https://ftp.pride.ebi.ac.uk/") for f in p.files)


def test_pdc_categories_and_signed_urls(cfg, http):
    cats = browse(cfg, "cptac-pdc", {"pdc_study_id": "PDC000127"}, http)["categories"]
    assert "Protein Assembly" in cats and "Raw Mass Spectra" in cats
    p = plan_dataset(cfg, "cptac-pdc", {"pdc_study_id": "PDC000127", "data_categories": ["Protein Assembly"]},
                     None, None, None, None, http)
    assert p.files and all(f.checksum_type == "md5" and "Signature=" in f.url for f in p.files)
    assert p.dest.endswith("proteomics/cptac/PDC000127")


def test_sea_ad_browse_and_plan(cfg, http):
    assert "MTG/" in browse(cfg, "sea-ad", {}, http)["subfolders"]
    p = plan_dataset(cfg, "sea-ad", {"prefix": "MTG/RNAseq/Changelog"}, None, None, None, None, http)
    assert [f.relpath for f in p.files] == ["MTG/RNAseq/Changelog.html"]


def test_tahoe_metadata_listing(cfg, http):
    p = plan_dataset(cfg, "tahoe-100m", {"path": "metadata"}, None, None, None, None, http)
    assert p.files and all(f.relpath.startswith("metadata/") for f in p.files)
    assert p.meta["license"] == "cc0-1.0"


def test_cellxgene_sea_ad_collection(cfg, http):
    p = plan_dataset(cfg, "cellxgene-discover", {"collection_id": "1ca90a2d-2943-483d-b678-b809bf464c30"},
                     None, None, None, 5, http)
    assert len(p.files) == 5 and all(f.relpath.endswith(".h5ad") and f.size for f in p.files)


def test_scperturb_zenodo(cfg, http):
    p = plan_dataset(cfg, "scperturb", {}, None, ["*Norman*"], None, None, http)
    assert p.files and all(f.checksum_type == "md5" for f in p.files)


@pytest.fixture
def live_aria2(cfg, tmp_path):
    if not shutil.which("aria2c"):
        pytest.skip("aria2c not installed")
    port, secret = 16800 + os.getpid() % 1000, "live-secret"
    (tmp_path / "s").write_text(secret)
    extra = [f"--ca-certificate={os.environ['ARIA2_CA']}"] if os.environ.get("ARIA2_CA") else []
    p = subprocess.Popen(["aria2c", "--enable-rpc", f"--rpc-listen-port={port}", f"--rpc-secret={secret}",
                          "--quiet=true", *extra])
    cfg.aria2_url, cfg.aria2_secret_file = f"http://127.0.0.1:{port}/jsonrpc", tmp_path / "s"
    time.sleep(1)
    yield cfg
    p.terminate()


def test_real_small_downloads_verified(live_aria2, http):
    cfg = live_aria2
    plans = [
        plan_dataset(cfg, "sea-ad", {"prefix": "MTG/RNAseq/Changelog"}, None, None, None, None, http),  # S3, md5 ETag
        plan_dataset(cfg, "tahoe-100m", {"path": "metadata"}, None, ["*.parquet"], None, 1, http),  # HF, sha256
        plan_dataset(cfg, "pride", {"accession": "PXD000001"}, None, ["*.mztab.gz"], None, 1, http),  # PRIDE https
    ]
    for p in plans:
        assert p.known_bytes < 50 * 1024**2, p.summary()
        job = jobs.submit(cfg, p)["job_id"]
        for _ in range(240):
            st = jobs.status(cfg, job)
            if st["state"] in ("complete", "error"):
                break
            time.sleep(0.5)
        assert st["state"] == "complete", st
        v = verify.run(cfg, job)
        assert v["result"] == "ok", v
