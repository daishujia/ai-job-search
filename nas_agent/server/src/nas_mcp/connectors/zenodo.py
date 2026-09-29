"""Zenodo records (e.g. scPerturb harmonized h5ad files)."""
from __future__ import annotations

from ..manifest import FileEntry
from .base import Listing, require


def list_files(params: dict, http, cfg) -> Listing:
    rid = require(params, "record_id", r"\d{4,10}", "7041849")
    rec = http.get_json(f"https://zenodo.org/api/records/{rid}")
    files = []
    for f in rec.get("files", []):
        algo, _, digest = (f.get("checksum") or "").partition(":")
        files.append(FileEntry(
            url=f["links"]["self"], relpath=f["key"], size=f.get("size"),
            checksum_type="md5" if algo == "md5" and digest else None,
            checksum=digest if algo == "md5" and digest else None,
        ))
    md = rec.get("metadata", {})
    lic = md.get("license")
    return Listing(files=files, record=rec, meta={
        "title": md.get("title"), "license": lic.get("id") if isinstance(lic, dict) else lic,
        "doi": rec.get("doi"), "source_url": rec.get("links", {}).get("html", f"https://zenodo.org/records/{rid}"),
        "version": md.get("version"),
    })
