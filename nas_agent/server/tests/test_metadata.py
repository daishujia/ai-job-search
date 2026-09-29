import errno
import gzip
import json
import os
import zipfile
from pathlib import Path

import pytest

from nas_mcp import NasError, ingest, registry
from nas_mcp.layout import classify, project_location, resolve_project
from nas_mcp.manifest import FileEntry
from nas_mcp.metadata import extract, index, inspect as insp, ontology, schema, service
from nas_mcp.paths import resolve_dest, to_client, to_nas

from .conftest import FakeHttp

# trimmed real API records (PRIDE PXD046444, PDC PDC000127, CELLxGENE SEA-AD) captured 2026-09-29
PRIDE_REC = {
    "title": "Ultra-fast label-free quantification ... narrow-window DIA", "projectDescription": "Three species mix <b>benchmark</b>",
    "license": "Creative Commons Public Domain (CC0)", "keywords": ["Dia", "Astral"],
    "organisms": [{"accession": "NEWT:4932", "name": "Saccharomyces cerevisiae (baker's yeast)"},
                  {"accession": "NEWT:9606", "name": "Homo sapiens (Human)"}],
    "organismParts": [], "diseases": [],
    "instruments": [{"cvLabel": "MS", "accession": "MS:1003378", "name": "Orbitrap Astral"}],
    "experimentTypes": [{"accession": "PRIDE:0000450", "name": "Data-independent acquisition"}],
    "softwares": [{"accession": "MS:1003253", "name": "DIA-NN"}], "quantificationMethods": [],
    "references": [{"pubmedID": 0, "doi": "10.1038/S41587-023-02099-7"}],
    "labPIs": [{"firstName": "Jesper", "lastName": "V", "affiliation": "University of Copenhagen", "email": "x@y"}],
}
PDC_REC = {"study": {"study_id": "dbe94609", "pdc_study_id": "PDC000127", "study_name": "CPTAC CCRCC Discovery Study - Proteome",
                     "program_name": "Clinical Proteomic Tumor Analysis Consortium", "disease_type": "Clear Cell Renal Cell Carcinoma;Other",
                     "primary_site": "Kidney;Not Reported", "analytical_fraction": "Proteome", "experiment_type": "TMT10",
                     "cases_count": 124, "aliquots_count": 208}}
PDC_BIOS = [{"aliquot_submitter_id": "CPT0026410003", "case_submitter_id": "C3L-00791", "sample_submitter_id": "C3L-00791-01",
             "sample_type": "Primary Tumor", "disease_type": "Clear Cell Renal Cell Carcinoma", "primary_site": "Kidney",
             "taxon": "Homo sapiens", "pool": "No", "aliquot_id": "bd34"},
            {"aliquot_submitter_id": "CPT0026420003", "case_submitter_id": "C3L-00791", "sample_submitter_id": "C3L-00791-06",
             "sample_type": "Solid Tissue Normal", "disease_type": "Clear Cell Renal Cell Carcinoma", "primary_site": "Kidney",
             "taxon": "Homo sapiens", "pool": "No", "aliquot_id": "bd35"}]
CXG_REC = {"name": "SEA-AD: Seattle Alzheimer's Disease Brain Cell Atlas", "doi": "10.1038/s41593-024-01774-5",
           "collection_url": "https://cellxgene.cziscience.com/collections/1ca90a2d", "consortia": ["SEA-AD"],
           "publisher_metadata": {"authors": [{"family": "Gabitto", "given": "M"}]},
           "datasets": [{"dataset_id": "feea960d-aaaa", "title": "Sst Chodl - DLPFC", "cell_count": 1877,
                         "assay": [{"label": "10x 3' v3", "ontology_term_id": "EFO:0009922"}],
                         "disease": [{"label": "dementia", "ontology_term_id": "MONDO:0001627"},
                                     {"label": "normal", "ontology_term_id": "PATO:0000461"}],
                         "organism": [{"label": "Homo sapiens", "ontology_term_id": "NCBITaxon:9606"}],
                         "tissue": [{"label": "dorsolateral prefrontal cortex", "ontology_term_id": "UBERON:0009834"}],
                         "cell_type": [{"label": "sst GABAergic interneuron", "ontology_term_id": "CL:4023017"}],
                         "sex": [{"label": "female", "ontology_term_id": "PATO:0000383"}],
                         "suspension_type": ["nucleus"], "donor_id": ["H20.33.001", "H20.33.040"], "schema_version": "7.1.0"}]}


def _project(cfg, source, code, connector=None, record=None, plan=None):
    p = cfg.omics_root / source / code
    (p / "metadata" / "source").mkdir(parents=True)
    if connector:
        (p / "metadata/source" / f"{connector}.json").write_text(json.dumps(record))
    if plan:
        (p / "metadata/source/_plan.json").write_text(json.dumps(plan))
    return p


# ------------------------------------------------------------- layout & paths
@pytest.mark.parametrize("name,conn,attrs,level", [
    ("a.raw", "pride", {"category": "RAW"}, "raw"), ("x.sdrf.tsv", "pride", {"category": "EXPERIMENTAL DESIGN"}, "metadata"),
    ("DIANN.zip", "pride", {"category": "SEARCH"}, "processed"), ("p.tsv", "pdc", {"category": "Protein Assembly"}, "processed"),
    ("r.raw", "pdc", {"category": "Raw Mass Spectra"}, "raw"), ("s.mzML.gz", "", {}, "raw"), ("run.d/analysis.tdf", "", {}, "raw"),
    ("reads_R1.fastq.gz", "", {}, "raw"), ("x.h5ad", "", {}, "processed"), ("README.md", "", {}, "metadata"),
    ("sample_info.csv", "", {}, "metadata"), ("counts.parquet", "", {}, "processed"), ("plate1.ome.tiff", "", {}, "raw")])
def test_classify(name, conn, attrs, level):
    assert classify(FileEntry(url="", relpath=name, attrs=attrs), conn) == level


def test_project_location_templates(cfg):
    get = lambda i: registry.get(cfg, i)  # noqa: E731
    assert project_location(cfg, get("pride"), {"accession": "PXD046444"})[:2] == ("PRIDE", "PXD046444")
    assert project_location(cfg, get("sea-ad"), {"prefix": "MTG/RNAseq/"})[:2] == ("SEA-AD", "MTG")
    assert project_location(cfg, get("cellxgene-census"), {"prefix": "cell-census/2025-01-30/h5ads/"})[:2] == \
        ("CELLxGENE-Census", "2025-01-30")
    assert project_location(cfg, get("tahoe-100m"), {})[:2] == ("Tahoe", "Tahoe-100M")
    with pytest.raises(NasError, match="project code"):
        project_location(cfg, get("depmap"), {})
    assert project_location(cfg, get("depmap"), {}, project_code="24Q4")[1] == "24Q4"
    assert project_location(cfg, get("open-urls"), {}, "GSE157827", "GEO")[:2] == ("GEO", "GSE157827")
    with pytest.raises(NasError, match="fixed"):
        project_location(cfg, get("pride"), {"accession": "PXD046444"}, source="Mine")
    assert project_location(cfg, get("open-urls"), {}, "../x", "GEO")[1] == "x"  # sanitised, cannot traverse
    assert project_location(cfg, get("open-urls"), {}, "a b/c", "GEO")[1] == "a_b_c"


def test_mac_paths_map_to_nas_and_back(cfg):
    mac = "/Volumes/AI4Sci/database/PRIDE/PXD046444"
    nas = to_nas(cfg, mac)
    assert nas == f"{cfg.omics_root}/PRIDE/PXD046444" and to_client(cfg, nas) == mac
    assert resolve_dest(cfg, mac) == (cfg.omics_root / "PRIDE/PXD046444").resolve()
    (cfg.omics_root / "PRIDE/PXD046444").mkdir(parents=True)
    assert resolve_project(cfg, mac) == resolve_project(cfg, "PRIDE/PXD046444")
    with pytest.raises(NasError, match="SOURCE"):
        resolve_project(cfg, "PRIDE")


# ------------------------------------------------------------- extraction
def test_extract_pride_with_sdrf(cfg):
    p = _project(cfg, "PRIDE", "PXD046444", "pride", PRIDE_REC, {"dataset_id": "pride", "policy": "allowed",
                                                                  "meta": {"title": "t", "license": "CC0"}})
    (p / "metadata" / "PXD046444.sdrf.tsv").write_text(
        "source name\tcharacteristics[organism]\tcharacteristics[organism part]\tcharacteristics[disease]\t"
        "characteristics[biological replicate]\tcomment[data file]\tcomment[label]\tfactor value[spiked compound]\n"
        "S1\thomo sapiens\tnot applicable\tnormal\t1\ta.raw\tlabel free sample\tE5H50Y45\n"
        "S2\thomo sapiens\tnot applicable\tnormal\t2\tb.raw\tlabel free sample\tE30H50Y20\n")
    (p / "raw").mkdir()
    (p / "raw" / "a.raw").write_bytes(b"x" * 10)
    r = service.extract_draft(cfg, "PRIDE/PXD046444", online=False)
    st = r["study"]
    assert r["schema_errors"] == []
    assert {t.get("id") for t in st["biology"]["organism"]} == {"NCBITaxon:4932", "NCBITaxon:9606"}
    assert st["biology"]["organism"][1]["label"] == "Homo sapiens"
    assert st["assay"]["technology"] == [{"label": "Orbitrap Astral", "id": "MS:1003378", "ontology": "MS"}]
    assert st["assay"]["acquisition"] == ["DIA"] and st["identity"]["description"] == "Three species mix benchmark"
    assert st["identity"]["publications"][0] == {"pmid": None, "doi": "10.1038/S41587-023-02099-7", "citation": None}
    assert "email" not in json.dumps(st["identity"]["contacts"])  # personal emails are not copied
    assert r["samples_rows"] == 2 and st["design"]["n_samples"] == 2
    rows = schema.read_samples(p / "metadata" / "samples.draft.tsv")
    assert rows[0]["sample_id"] == "S1" and rows[0]["disease"] == "normal" and rows[0]["condition"] == "E5H50Y45"
    assert rows[0]["data_file"] == "a.raw" and rows[0]["replicate"] == "1"
    assert st["data"]["levels"]["raw"] == {"files": 1, "bytes": 10, "formats": [".raw"]}
    assert st["data"]["client_path"] == "/Volumes/AI4Sci/database/PRIDE/PXD046444"
    assert "biology.sample_type" in r["gaps"]
    assert index.query(cfg, filters={"organism": "NCBITaxon:4932"})[0]["project_code"] == "PXD046444"


def test_extract_pdc_with_biospecimens(cfg):
    p = _project(cfg, "CPTAC-PDC", "PDC000127", "pdc", PDC_REC, {"dataset_id": "cptac-pdc", "policy": "allowed"})
    (p / "metadata/source/biospecimens.json").write_text(json.dumps(PDC_BIOS))
    r = service.extract_draft(cfg, p, online=False)
    st = r["study"]
    assert r["schema_errors"] == [] and r["samples_rows"] == 2
    assert [t["label"] for t in st["biology"]["disease"]] == ["Clear Cell Renal Cell Carcinoma"]
    assert [t["label"] for t in st["biology"]["sample_type"]] == ["Primary Tumor", "Solid Tissue Normal"]
    assert st["design"]["n_subjects"] == 124 and st["assay"]["quantification"] == ["TMT10"]
    assert st["assay"]["modality"] == ["ms_proteomics"]
    rows = schema.read_samples(p / "metadata/samples.draft.tsv")
    assert rows[0]["subject_id"] == "C3L-00791" and rows[1]["sample_type"] == "Solid Tissue Normal"
    assert list(rows[0])[:2] == ["sample_id", "subject_id"] and "char:pool" in rows[0]


@pytest.mark.parametrize("types,acq", [(["Data-independent acquisition"], ["DIA"]), (["Data-dependent acquisition"], ["DDA"]),
                                       (["Bottom-up proteomics", "TMT"], ["TMT"]), (["Parallel reaction monitoring"], ["PRM"])])
def test_pride_acquisition_mapping(cfg, types, acq):
    st = {"identity": {"title": "t"}, "biology": {}, "assay": {"modality": ["ms_proteomics"]}, "extensions": {}}
    extract.from_pride({**PRIDE_REC, "experimentTypes": [{"name": t} for t in types]}, st, {})
    assert st["assay"]["acquisition"] == acq


def test_extract_cellxgene(cfg):
    _project(cfg, "CELLxGENE", "1ca90a2d", "cellxgene", CXG_REC, {"dataset_id": "cellxgene-discover", "policy": "allowed"})
    st = service.extract_draft(cfg, "CELLxGENE/1ca90a2d", online=False)["study"]
    assert schema.validate(st) == []
    assert {t["id"] for t in st["biology"]["disease"]} == {"MONDO:0001627", "PATO:0000461"}
    assert st["assay"]["modality"] == ["snRNA-seq"] and st["design"]["n_cells"] == 1877 and st["design"]["n_subjects"] == 2
    assert st["assay"]["technology"][0]["id"] == "EFO:0009922"
    assert st["curation"]["field_evidence"]["biology.cell_type"]["source"] == "api"


def test_schema_rejects_bad_records(cfg):
    _project(cfg, "CELLxGENE", "c1", "cellxgene", CXG_REC)
    st = service.extract_draft(cfg, "CELLxGENE/c1", online=False)["study"]
    bad = json.loads(json.dumps(st))
    bad["assay"]["modality"] = ["telepathy"]
    bad["biology"]["disease"] = [{"label": "AD", "id": "not an id"}]
    bad["identity"]["title"] = ""
    errs = schema.validate(bad)
    assert any("assay/modality" in e for e in errs) and any("biology/disease/0/id" in e for e in errs)
    assert any("identity/title" in e for e in errs)


# ------------------------------------------------------------- save / index / query
def test_save_validates_indexes_and_queries(cfg):
    p = _project(cfg, "CPTAC-PDC", "PDC000127", "pdc", PDC_REC, {"dataset_id": "cptac-pdc", "policy": "allowed"})
    (p / "metadata/source/biospecimens.json").write_text(json.dumps(PDC_BIOS))
    st = service.extract_draft(cfg, p, online=False)["study"]
    bad = json.loads(json.dumps(st))
    bad["assay"]["modality"] = []
    r = service.save(cfg, "CPTAC-PDC/PDC000127", bad)
    assert r["saved"] is False and not (p / "metadata/study.json").exists()
    wrong = json.loads(json.dumps(st))
    wrong["identity"]["project_code"] = "PDC999999"
    with pytest.raises(NasError, match="must be"):
        service.save(cfg, "CPTAC-PDC/PDC000127", wrong)

    st["biology"]["disease"] = [{"label": "clear cell renal carcinoma", "id": "MONDO:0005005", "ontology": "MONDO",
                                 "verbatim": "Clear Cell Renal Cell Carcinoma"}]
    st["biology"]["sample_type"] = [{"label": "tumor tissue"}, {"label": "normal adjacent tissue"}]
    st["design"]["study_type"] = "case-control"
    st["curation"]["field_evidence"]["biology.disease"] = {"source": "inferred", "detail": "OLS4 exact match",
                                                          "confidence": "high"}
    r = service.save(cfg, "/Volumes/AI4Sci/database/CPTAC-PDC/PDC000127", st)
    assert r["saved"] is True and r["samples_rows"] == 2  # draft samples carried over
    saved = json.loads((p / "metadata/study.json").read_text())
    assert saved["curation"]["status"] == "curated" and saved["data"]["has_samples_table"] is True
    assert index.query(cfg, filters={"disease": "MONDO:0005005"})[0]["metadata_status"] == "curated"
    assert index.query(cfg, filters={"disease": "renal", "modality": "ms_proteomics"})
    assert index.query(cfg, filters={"disease": "alzheimer"}) == []
    assert index.query(cfg, text="CPTAC TMT10")
    cat = (cfg.omics_root / "CATALOG.tsv").read_text().splitlines()
    assert cat[0].startswith("source\tproject_code") and "clear cell renal carcinoma" in cat[1]
    assert "/Volumes/AI4Sci/database/CPTAC-PDC/PDC000127" in cat[1]
    # rebuild from disk gives the same answer (curated record wins over draft)
    (cfg.catalog_dir / "catalog.sqlite").unlink()
    assert index.rebuild(cfg)["indexed"] == 1
    assert index.query(cfg, filters={"disease": "MONDO:0005005"})


# ------------------------------------------------------------- inspection
def test_inspect_files(cfg):
    p = cfg.omics_root / "X" / "y"
    (p / "processed").mkdir(parents=True)
    (p / "metadata").mkdir()
    (p / "processed/prot.tsv").write_text("Protein\tGroup\tNPX\nAPP\tAD\t1.2\nMAPT\tCTL\t0.4\n")
    with gzip.open(p / "processed/pep.csv.gz", "wt") as fh:
        fh.write("peptide,charge\nPEPTIDE,2\n")
    (p / "processed/res.mzTab").write_text("MTD\tmzTab-version\t1.0.0\nMTD\tms_run[1]-location\tfile://a.raw\nPRH\taccession\n")
    with zipfile.ZipFile(p / "processed/DIANN.zip", "w") as z:
        z.writestr("report.tsv", "x")
    (p / "metadata/s.sdrf.tsv").write_text("source name\tcharacteristics[disease]\nS1\tAD\nS2\tcontrol\n")
    res = {Path(r["path"]).name: r for r in service.inspect_files(cfg, "X/y")["files"]}
    assert res["prot.tsv"]["columns"] == ["Protein", "Group", "NPX"] and res["prot.tsv"]["categorical_columns"]["Group"] == ["AD", "CTL"]
    assert res["pep.csv.gz"]["delimiter"] == "comma"
    assert res["res.mzTab"]["metadata"]["ms_run[1]-location"] == "file://a.raw"
    assert res["DIANN.zip"]["entries"] == ["report.tsv"]
    assert res["s.sdrf.tsv"]["characteristics"]["characteristics[disease]"] == ["AD", "control"]


def test_inspect_h5ad_and_parquet(tmp_path):
    h5py = pytest.importorskip("h5py")
    pa = pytest.importorskip("pyarrow")
    import pyarrow.parquet as pq
    f = tmp_path / "x.h5ad"
    with h5py.File(f, "w") as h:
        obs = h.create_group("obs")
        obs.attrs["_index"] = "_index"
        obs["_index"] = [b"c1", b"c2", b"c3"]
        ct = obs.create_group("cell_type")
        ct["categories"] = [b"neuron", b"astrocyte"]
        ct["codes"] = [0, 1, 0]
        var = h.create_group("var")
        var.attrs["_index"] = "_index"
        var["_index"] = [b"APP", b"MAPT"]
        uns = h.create_group("uns")
        uns["schema_version"] = "5.2.0"
    r = insp.inspect_h5ad(f)
    assert (r["n_obs"], r["n_vars"]) == (3, 2) and r["obs_categories"]["cell_type"] == ["neuron", "astrocyte"]
    assert r["cellxgene_schema_version"] == "5.2.0"
    pq.write_table(pa.table({"gene": ["A"], "value": [1.0]}), tmp_path / "t.parquet")
    assert insp.inspect_parquet(tmp_path / "t.parquet") == {"kind": "parquet", "n_rows": 1, "columns": ["gene", "value"]}


# ------------------------------------------------------------- ontology
def test_ontology_fixed_and_ols(cfg):
    assert ontology.lookup(None, "sample_type", "Plasma")["candidates"][0]["id"] == "UBERON:0001969"
    docs = {"response": {"docs": [
        {"label": "renal cell carcinoma", "obo_id": "MONDO:0005086", "ontology_name": "mondo", "synonym": []},
        {"label": "clear cell renal carcinoma", "obo_id": "MONDO:0005005", "ontology_name": "mondo",
         "synonym": ["clear cell renal cell carcinoma"]}]}}
    r = ontology.lookup(FakeHttp({"ols4": docs}), "disease", "Clear Cell Renal Cell Carcinoma")
    assert r["candidates"][0]["id"] == "MONDO:0005005" and r["candidates"][0]["exact"]
    assert ontology.newt_to_ncbitaxon("NEWT:9606") == "NCBITaxon:9606"


# ------------------------------------------------------------- local ingest
def _downloads(cfg, tmp_path):
    dl = cfg.omics_root.parent / "Downloads" / "adni_export"
    (dl / "sub").mkdir(parents=True)
    (dl / "CSF_proteomics.csv").write_text("RID,APP\n1,2\n")
    (dl / "sub" / "scan.fastq.gz").write_bytes(b"@r\nACGT\n")
    (dl / "README.txt").write_text("export notes")
    cfg.allowed_roots.append(cfg.omics_root.parent / "Downloads")
    return dl


def test_ingest_move_plan_apply(cfg, tmp_path):
    dl = _downloads(cfg, tmp_path)
    with pytest.raises(NasError, match="Nothing was queued"):
        ingest.plan_ingest(cfg, str(dl), "UKB", "x", dataset_id="ukb-ppp-individual")
    plan = ingest.plan_ingest(cfg, str(dl), "ADNI", "ADNI3-CSF", "move", dataset_id="adni")
    assert plan["files"] == 3 and set(plan["by_level"]) == {"processed", "raw", "metadata"}
    assert plan["to_client"] == "/Volumes/AI4Sci/database/ADNI/ADNI3-CSF" and plan["same_filesystem"]
    assert (dl / "CSF_proteomics.csv").exists()  # dry run touched nothing
    with pytest.raises(NasError, match="confirm=true"):
        ingest.apply_ingest(cfg, plan["ingest_id"], confirm=False)
    with pytest.raises(NasError, match="policy_ack"):
        ingest.apply_ingest(cfg, plan["ingest_id"], confirm=True)
    r = ingest.apply_ingest(cfg, plan["ingest_id"], confirm=True, policy_ack="ADNI DUA (personal), local copy allowed")
    proj = cfg.omics_root / "ADNI" / "ADNI3-CSF"
    assert r["transferred"] == 3 and not (dl / "CSF_proteomics.csv").exists()
    assert (proj / "processed/CSF_proteomics.csv").exists() and (proj / "raw/sub/scan.fastq.gz").exists()
    assert (proj / "metadata/README.txt").exists() and (proj / "files.tsv").exists()
    assert r["metadata_draft"] == "metadata/study.draft.json"
    with pytest.raises(NasError, match="already applied"):
        ingest.apply_ingest(cfg, plan["ingest_id"], confirm=True, policy_ack="x" * 10)


def test_ingest_copy_never_overwrites_and_exdev(cfg, tmp_path, monkeypatch):
    dl = _downloads(cfg, tmp_path)
    proj = cfg.omics_root / "GEO" / "GSE1"
    (proj / "processed").mkdir(parents=True)
    (proj / "processed/CSF_proteomics.csv").write_text("keep me")
    plan = ingest.plan_ingest(cfg, str(dl), "GEO", "GSE1", "copy")
    assert plan["existing_targets_skipped"] == 1
    r = ingest.apply_ingest(cfg, plan["ingest_id"], confirm=True)
    assert r["transferred"] == 2 and (proj / "processed/CSF_proteomics.csv").read_text() == "keep me"
    assert (dl / "README.txt").exists()  # copy leaves the source

    def cross_device(a, b):
        raise OSError(errno.EXDEV, "Invalid cross-device link")
    monkeypatch.setattr(os, "rename", cross_device)
    plan2 = ingest.plan_ingest(cfg, str(dl), "GEO", "GSE2", "move")
    r2 = ingest.apply_ingest(cfg, plan2["ingest_id"], confirm=True)
    assert r2["transferred"] == 0 and "mode=copy" in r2["failed"][0]["hint"]
