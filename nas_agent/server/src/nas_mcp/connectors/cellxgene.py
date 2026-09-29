"""CZ CELLxGENE Discover curation API: download per-dataset H5AD/RDS assets.

Either a collection_id (e.g. SEA-AD 1ca90a2d-2943-483d-b678-b809bf464c30) or filters over
all public datasets (disease / tissue / assay / organism substrings; at least one required).
"""
from __future__ import annotations

from .. import NasError
from ..manifest import FileEntry
from ..paths import slug
from .base import Listing

API = "https://api.cellxgene.cziscience.com/curation/v1"


def _labels(v) -> str:
    if isinstance(v, list):
        return " | ".join(x.get("label", "") if isinstance(x, dict) else str(x) for x in v)
    return str(v or "")


def list_files(params: dict, http, cfg) -> Listing:
    cid = str(params.get("collection_id") or "").strip()
    filters = {k: str(params[k]).lower() for k in ("disease", "tissue", "assay", "organism", "cell_type")
               if params.get(k)}
    filetype = str(params.get("filetype") or "H5AD").upper()
    if cid:
        coll = http.get_json(f"{API}/collections/{cid}")
        datasets, title = coll.get("datasets", []), coll.get("name")
        src = f"https://cellxgene.cziscience.com/collections/{cid}"
    elif filters:
        datasets, title, src = http.get_json(f"{API}/datasets"), "CELLxGENE filtered datasets", API
    else:
        raise NasError("Give collection_id, or at least one of disease/tissue/assay/organism/cell_type filters.")
    files, matched = [], []
    for d in datasets:
        if any(v not in _labels(d.get(k)).lower() for k, v in filters.items()):
            continue
        matched.append(d)
        for a in d.get("assets", []):
            if a.get("filetype", "").upper() != filetype:
                continue
            ext = ".h5ad" if filetype == "H5AD" else ".rds"
            files.append(FileEntry(
                url=a["url"], relpath=f"{slug(d.get('title') or 'dataset', 60)}_{d['dataset_id'][:8]}{ext}",
                size=a.get("filesize"),
                attrs={"dataset_id": d["dataset_id"], "title": d.get("title"),
                       "cell_count": d.get("cell_count"), "disease": _labels(d.get("disease"))[:200],
                       "tissue": _labels(d.get("tissue"))[:200], "assay": _labels(d.get("assay"))[:200]},
            ))
    record = ({k: v for k, v in coll.items() if k != "datasets"} if cid else {"filters": filters})
    record["datasets"] = matched
    return Listing(files=files, record=record, meta={
        "title": title, "source_url": src, "filters": filters,
        "license": "CC BY 4.0 (CELLxGENE Discover datasets; confirm per collection)",
    })
