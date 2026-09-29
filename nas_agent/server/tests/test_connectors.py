import pytest

from nas_mcp import NasError
from nas_mcp.connectors import cellxgene, huggingface, massive, pdc, pride, s3, urls, zenodo
from nas_mcp.manifest import FileEntry, apply_filters
from nas_mcp.planning import plan_dataset

from .conftest import FakeHttp

PRIDE_FILES = [
    {"fileName": "a.raw", "fileSizeBytes": 100, "checksum": "e8a70d96d0920d40ccfd4ca7d962dc32e587e736",
     "fileCategory": {"value": "RAW"},
     "publicFileLocations": [{"name": "FTP Protocol", "value": "ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2023/01/PXD1/a.raw"}]},
    {"fileName": "b.mztab", "fileSizeBytes": 5, "checksum": "", "fileCategory": {"value": "RESULT"},
     "publicFileLocations": [{"name": "FTP Protocol", "value": "ftp://ftp.pride.ebi.ac.uk/x/b.mztab"}]},
]


def test_pride(cfg):
    http = FakeHttp({"/files/all": PRIDE_FILES, "/projects/PXD046444": {"title": "T\n", "license": "CC0"}})
    L = pride.list_files({"accession": "PXD046444"}, http, cfg)
    a = L.files[0]
    assert a.url.startswith("https://ftp.pride.ebi.ac.uk/") and a.checksum_type == "sha-1"
    assert a.relpath == "a.raw" and a.attrs["category"] == "RAW" and a.size_exact is False
    assert L.files[1].checksum is None
    assert len(pride.list_files({"accession": "PXD046444", "categories": ["result"]}, http, cfg).files) == 1
    with pytest.raises(NasError, match="PXD"):
        pride.list_files({"accession": "PXD1"}, http, cfg)


def _pdc_http():
    files = [{"file_id": "f1", "file_name": "p.tsv", "file_size": "10", "md5sum": "AB" * 16,
              "data_category": "Protein Assembly"},
             {"file_id": "f2", "file_name": "r.raw", "file_size": "99", "md5sum": "", "data_category": "Raw Mass Spectra"}]

    def route(url, payload):
        q = payload["query"]
        if "study(" in q:
            return {"data": {"study": [{"study_id": "uuid-1", "study_name": "CCRCC", "disease_type": "x", "primary_site": "y"}]}}
        if "signedUrl" in q:
            assert 'data_category: "Protein Assembly"' in q
            return {"data": {"filesPerStudy": [{"file_id": "f1", "file_name": "p.tsv", "signedUrl": {"url": "https://cdn/p.tsv?sig=1"}}]}}
        assert 'study_id: "uuid-1"' in q
        return {"data": {"filesPerStudy": files}}
    return FakeHttp({"graphql": route})


def test_pdc_requires_categories_then_resolves(cfg):
    http = _pdc_http()
    with pytest.raises(NasError, match="Protein Assembly"):
        pdc.list_files({"pdc_study_id": "PDC000127"}, http, cfg)
    L = pdc.list_files({"pdc_study_id": "PDC000127", "data_categories": ["Protein Assembly"]}, http, cfg)
    assert [(f.relpath, f.size, f.checksum) for f in L.files] == [("Protein Assembly/p.tsv", 10, "ab" * 16)]
    with pytest.raises(NasError, match="Unknown data_categories"):
        pdc.list_files({"pdc_study_id": "PDC000127", "data_categories": ["Nope"]}, http, cfg)


S3_P1 = """<?xml version="1.0"?><ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
<IsTruncated>true</IsTruncated><NextContinuationToken>TOK</NextContinuationToken>
<Contents><Key>MTG/</Key><ETag>"d41d8cd98f00b204e9800998ecf8427e"</ETag><Size>0</Size></Contents>
<Contents><Key>MTG/a b.h5ad</Key><ETag>"f47423ede51f1aab1b9d85d2d2bbc0f1"</ETag><Size>12</Size></Contents>
</ListBucketResult>"""
S3_P2 = """<?xml version="1.0"?><ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
<IsTruncated>false</IsTruncated>
<Contents><Key>MTG/big.h5ad</Key><ETag>"0123456789abcdef0123456789abcdef-12"</ETag><Size>99</Size></Contents>
</ListBucketResult>"""


def test_s3_pagination_and_multipart_etag(cfg):
    http = FakeHttp({"continuation-token=TOK": S3_P2, "list-type=2": S3_P1})
    L = s3.list_files({"bucket": "sea-ad-single-cell-profiling", "region": "us-west-2", "prefix": "MTG/"}, http, cfg)
    assert [f.relpath for f in L.files] == ["MTG/a b.h5ad", "MTG/big.h5ad"]
    assert L.files[0].url.endswith("/MTG/a%20b.h5ad") and L.files[0].checksum_type == "md5"
    assert L.files[0].attrs == {"advisory_checksum": True}
    assert L.files[1].checksum is None  # multipart ETag is not an MD5


def test_hf_gated_needs_token(cfg):
    tree = [{"type": "directory", "path": "data"},
            {"type": "file", "path": "data/x.parquet", "size": 5, "lfs": {"oid": "c" * 64}}]
    http = FakeHttp({"/tree/": tree, "/api/datasets/org/ds": {"sha": "abc", "gated": False, "cardData": {"license": "cc0-1.0"}}})
    L = huggingface.list_files({"repo": "org/ds"}, http, cfg)
    assert L.files[0].url == "https://huggingface.co/datasets/org/ds/resolve/abc/data/x.parquet"
    assert L.files[0].checksum_type == "sha-256" and L.meta["license"] == "cc0-1.0"
    http.routes["/api/datasets/org/ds"] = {"sha": "abc", "gated": "auto"}
    with pytest.raises(NasError, match="gated"):
        huggingface.list_files({"repo": "org/ds"}, http, cfg)


def test_zenodo(cfg):
    rec = {"files": [{"key": "d.h5ad", "size": 3, "checksum": "md5:" + "a" * 32, "links": {"self": "https://zenodo.org/f"}}],
           "metadata": {"title": "scPerturb", "license": {"id": "cc-by-4.0"}}, "doi": "10.5281/x"}
    L = zenodo.list_files({"record_id": "7041849"}, FakeHttp({"records/7041849": rec}), cfg)
    assert L.files[0].checksum == "a" * 32 and L.meta["license"] == "cc-by-4.0"


def test_cellxgene_collection_and_filters(cfg):
    ds = [{"dataset_id": "feea960d-aaaa", "title": "Sst Chodl - DLPFC: SEA-AD", "disease": [{"label": "dementia"}],
           "tissue": [{"label": "dorsolateral prefrontal cortex"}], "assets": [
               {"filetype": "H5AD", "url": "https://datasets.cellxgene.cziscience.com/x.h5ad", "filesize": 7},
               {"filetype": "RDS", "url": "https://datasets.cellxgene.cziscience.com/x.rds", "filesize": 8}]}]
    http = FakeHttp({"collections/c1": {"name": "SEA-AD", "datasets": ds}, "/curation/v1/datasets": ds})
    L = cellxgene.list_files({"collection_id": "c1"}, http, cfg)
    assert [f.relpath for f in L.files] == ["Sst_Chodl_-_DLPFC_SEA-AD_feea960d.h5ad"]
    assert len(cellxgene.list_files({"disease": "dementia"}, http, cfg).files) == 1
    assert cellxgene.list_files({"disease": "parkinson"}, http, cfg).files == []
    with pytest.raises(NasError):
        cellxgene.list_files({}, http, cfg)


class FakeFTP:
    tree = {"/x01/MSV000079514": [("raw", {"type": "dir"}), ("README.txt", {"type": "file", "size": "4"})],
            "/x01/MSV000079514/raw": [("s1.raw", {"type": "file", "size": "1000"})]}

    def __init__(self, host, timeout=None):
        assert host == "massive.ucsd.edu"

    def login(self):
        pass

    def mlsd(self, path, facts=None):
        return iter(self.tree[path])

    def quit(self):
        pass


class FakeFTPNoMLSD(FakeFTP):
    def mlsd(self, path, facts=None):
        import ftplib
        raise ftplib.error_perm("500 MLSD not understood")

    def nlst(self, path):
        return [n for n, _ in self.tree[path]]

    def size(self, full):
        import ftplib
        parent, name = full.rsplit("/", 1)
        facts = dict(self.tree[parent])[name]
        if facts["type"] == "dir":
            raise ftplib.error_perm("550 not a file")
        return int(facts["size"])


def test_massive_walk_without_mlsd(cfg):
    proxi = {"title": "t", "datasetLink": [{"name": "Dataset FTP location", "value": "ftp://massive.ucsd.edu/x01/MSV000079514"}]}
    L = massive.list_files({"accession": "MSV000079514"}, FakeHttp({"proxi": proxi}), cfg, ftp_factory=FakeFTPNoMLSD)
    assert {(f.relpath, f.size) for f in L.files} == {("raw/s1.raw", 1000), ("README.txt", 4)}


def test_massive_walk(cfg):
    proxi = {"title": "draft map", "datasetLink": [{"name": "Dataset FTP location", "value": "ftp://massive.ucsd.edu/x01/MSV000079514"}]}
    L = massive.list_files({"accession": "MSV000079514"}, FakeHttp({"proxi": proxi}), cfg, ftp_factory=FakeFTP)
    assert {(f.relpath, f.size) for f in L.files} == {("raw/s1.raw", 1000), ("README.txt", 4)}
    assert all(f.url.startswith("ftp://massive.ucsd.edu/x01/") for f in L.files)


def test_urls_validation(cfg):
    L = urls.list_files({"urls": ["https://h/a/file%201.tsv", {"url": "ftp://h/b", "md5": "A" * 32}]}, None, cfg)
    assert [f.relpath for f in L.files] == ["file 1.tsv", "b"] and L.files[1].checksum == "a" * 32
    for bad in (["file:///etc/passwd"], ["javascript:alert(1)"], [{"url": "https://h/x", "md5": "zz"}]):
        with pytest.raises(NasError):
            urls.list_files({"urls": bad}, None, cfg)


def test_filters_and_dedupe():
    fs = [FileEntry(url="u", relpath=p) for p in ["a/x.raw", "a/y.mzML", "b/x.raw", "a/x.raw"]]
    assert [f.relpath for f in apply_filters(fs, ["*.raw"], None, None)] == ["a/x.raw", "b/x.raw"]
    assert [f.relpath for f in apply_filters(fs, None, ["b/*"], 2)] == ["a/x.raw", "a/y.mzML"]


def test_plan_dataset_end_to_end_offline(cfg):
    http = FakeHttp({"/files/all": PRIDE_FILES, "/projects/PXD046444": {"title": "T", "license": "CC0"}})
    plan = plan_dataset(cfg, "pride", {"accession": "PXD046444"}, include=["*.raw"], http=http)
    assert plan.dest.endswith("omics/PRIDE/PXD046444") and [f.relpath for f in plan.files] == ["raw/a.raw"]
    s = plan.summary()
    assert s["policy"] == "allowed" and s["sizes_are_estimates"] and s["with_checksum"] == 1
    assert (s["source"], s["project_code"]) == ("PRIDE", "PXD046444") and s["levels"]["raw"]["files"] == 1
    both = plan_dataset(cfg, "pride", {"accession": "PXD046444"}, levels=["processed"], http=http)
    assert [f.relpath for f in both.files] == ["processed/b.mztab"]
    with pytest.raises(NasError, match="No files matched"):
        plan_dataset(cfg, "pride", {"accession": "PXD046444"}, include=["*.nothing"], http=http)
    with pytest.raises(NasError, match="project code"):
        plan_dataset(cfg, "open-s3", {"prefix": "x"}, http=FakeHttp({}))  # no bucket -> no network call either
    with pytest.raises(NasError, match="fixed"):
        plan_dataset(cfg, "pride", {"accession": "PXD046444"}, source="Other", http=http)
