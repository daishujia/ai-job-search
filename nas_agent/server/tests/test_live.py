"""Live checks against the real public APIs (network). Run: pytest -m live
Downloads are tiny (<1 MB each) and go through a real aria2c when available."""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

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
    p = plan_dataset(cfg, "pride", {"accession": "PXD000001"}, http=http)
    assert p.files and all(f.url.startswith("https://ftp.pride.ebi.ac.uk/") for f in p.files)


def test_pdc_categories_and_signed_urls(cfg, http):
    cats = browse(cfg, "cptac-pdc", {"pdc_study_id": "PDC000127"}, http)["categories"]
    assert "Protein Assembly" in cats and "Raw Mass Spectra" in cats
    p = plan_dataset(cfg, "cptac-pdc", {"pdc_study_id": "PDC000127", "data_categories": ["Protein Assembly"]}, http=http)
    assert p.files and all(f.checksum_type == "md5" and "Signature=" in f.url for f in p.files)
    assert p.dest.endswith("CPTAC-PDC/PDC000127") and all(f.relpath.startswith("processed/") for f in p.files)


def test_sea_ad_browse_and_plan(cfg, http):
    assert "MTG/" in browse(cfg, "sea-ad", {}, http)["subfolders"]
    p = plan_dataset(cfg, "sea-ad", {"prefix": "MTG/RNAseq/Changelog"}, http=http)
    assert [f.relpath for f in p.files] == ["metadata/MTG/RNAseq/Changelog.html"] and p.dest.endswith("SEA-AD/MTG")


def test_tahoe_metadata_listing(cfg, http):
    p = plan_dataset(cfg, "tahoe-100m", {"path": "metadata"}, http=http)
    assert p.files and p.dest.endswith("Tahoe/Tahoe-100M")
    assert p.meta["license"] == "cc0-1.0"


def test_cellxgene_sea_ad_collection(cfg, http):
    p = plan_dataset(cfg, "cellxgene-discover", {"collection_id": "1ca90a2d-2943-483d-b678-b809bf464c30"},
                     max_files=5, http=http)
    assert len(p.files) == 5 and all(f.relpath.startswith("processed/") and f.relpath.endswith(".h5ad") for f in p.files)
    assert p.dest.endswith("CELLxGENE/1ca90a2d-2943-483d-b678-b809bf464c30") and len(p.record["datasets"]) == 50


def test_scperturb_zenodo(cfg, http):
    p = plan_dataset(cfg, "scperturb", {}, include=["*Norman*"], http=http)
    assert p.files and all(f.checksum_type == "md5" for f in p.files)


@pytest.fixture
def live_aria2(cfg, tmp_path):
    if not shutil.which("aria2c"):
        pytest.skip("aria2c not installed")
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    secret = "live-secret"
    (tmp_path / "s").write_text(secret)
    extra = [f"--ca-certificate={os.environ['ARIA2_CA']}"] if os.environ.get("ARIA2_CA") else []
    p = subprocess.Popen(["aria2c", "--enable-rpc", f"--rpc-listen-port={port}", f"--rpc-secret={secret}",
                          "--quiet=true", *extra])
    cfg.aria2_url, cfg.aria2_secret_file = f"http://127.0.0.1:{port}/jsonrpc", tmp_path / "s"
    for _ in range(50):
        try:
            jobs.aria2_client(cfg).version()
            break
        except Exception:
            time.sleep(0.1)
    yield cfg
    p.terminate()
    p.wait()


def test_real_small_downloads_verified(live_aria2, http):
    cfg = live_aria2
    plans = [
        plan_dataset(cfg, "sea-ad", {"prefix": "MTG/RNAseq/Changelog"}, http=http),  # S3, md5 ETag
        plan_dataset(cfg, "tahoe-100m", {"path": "metadata"}, include=["*.parquet"], max_files=1, http=http),  # HF
        plan_dataset(cfg, "pride", {"accession": "PXD000001"}, include=["*.mztab.gz"], max_files=1, http=http),
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


# ---------------------------------------------------------------- metadata, live
def test_live_pride_sdrf_download_to_metadata(live_aria2, http):
    """Real PRIDE project: download only metadata (SDRF), verify -> automatic draft with real samples."""
    cfg = live_aria2
    p = plan_dataset(cfg, "pride", {"accession": "PXD046444"}, levels=["metadata"], http=http)
    assert [f.relpath for f in p.files] == ["metadata/PXD046444_community_annotated.sdrf.tsv"]
    job = jobs.submit(cfg, p)["job_id"]
    for _ in range(120):
        if jobs.status(cfg, job)["state"] in ("complete", "error"):
            break
        time.sleep(0.5)
    v = verify.run(cfg, job)
    assert v["result"] == "ok" and v["samples_rows"] > 10, v
    from nas_mcp.metadata import schema
    st = json.loads((Path(p.dest) / "metadata/study.draft.json").read_text())
    assert schema.validate(st) == [] and st["assay"]["technology"][0]["id"] == "MS:1003378"
    assert st["assay"]["acquisition"] == ["DIA"]


def test_live_pdc_biospecimens_and_cellxgene_extract(cfg, http):
    from nas_mcp.jobs import _save_source_records
    from nas_mcp.metadata import service
    for dsid, params in (("cptac-pdc", {"pdc_study_id": "PDC000127", "data_categories": ["Quality Metrics"]}),
                         ("cellxgene-discover", {"collection_id": "1ca90a2d-2943-483d-b678-b809bf464c30"})):
        plan = plan_dataset(cfg, dsid, params, max_files=1, http=http)
        Path(plan.dest).mkdir(parents=True, exist_ok=True)
        _save_source_records(plan, Path(plan.dest), None)
        r = service.extract_draft(cfg, plan.dest, http=http)
        assert r["schema_errors"] == [], r["schema_errors"]
        if dsid == "cptac-pdc":
            assert r["samples_rows"] == 208 and r["study"]["design"]["n_subjects"] == 124
        else:
            st = r["study"]
            assert "snRNA-seq" in st["assay"]["modality"] and st["design"]["n_cells"] > 1_000_000
            assert any(t.get("id") == "MONDO:0001627" for t in st["biology"]["disease"])


def test_live_ols_lookup(http):
    from nas_mcp.metadata import service
    r = service.lookup_terms([{"field": "disease", "text": "Clear Cell Renal Cell Carcinoma"},
                              {"field": "tissue", "text": "dorsolateral prefrontal cortex"},
                              {"field": "cell_type", "text": "astrocyte"}], http)
    ids = [x["candidates"][0]["id"] for x in r]
    assert ids[0].startswith("MONDO:") and ids[1] == "UBERON:0009834" and ids[2] == "CL:0000127"
