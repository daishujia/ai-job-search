"""PRIDE Archive (ProteomeXchange PXD accessions) via the v3 REST API."""
from __future__ import annotations

import re

from ..manifest import FileEntry
from .base import Listing, require

API = "https://www.ebi.ac.uk/pride/ws/archive/v3/projects"


def _https(loc: str) -> str:
    # PRIDE's FTP tree is also served over HTTPS with byte ranges -> resumable, multi-connection.
    return re.sub(r"^ftp://ftp\.pride\.ebi\.ac\.uk/", "https://ftp.pride.ebi.ac.uk/", loc)


def list_files(params: dict, http, cfg) -> Listing:
    acc = require(params, "accession", r"PXD\d{6}", "PXD046444")
    cats = {c.upper() for c in params.get("categories") or []}  # RAW, RESULT, SEARCH, PEAK, FASTA, OTHER
    project = http.get_json(f"{API}/{acc}")
    files = []
    for f in http.get_json(f"{API}/{acc}/files/all"):
        cat = (f.get("fileCategory") or {}).get("value", "OTHER")
        if cats and cat.upper() not in cats:
            continue
        locs = {l.get("name"): l.get("value") for l in f.get("publicFileLocations", [])}
        url = locs.get("FTP Protocol")
        if not url:
            continue
        chk = (f.get("checksum") or "").lower()
        files.append(FileEntry(
            url=_https(url),
            relpath=f"{cat}/{f['fileName']}",
            size=f.get("fileSizeBytes"),
            size_exact=False,  # PRIDE sizes are indicative (observed mismatches on older projects)
            checksum_type="sha-1" if re.fullmatch(r"[0-9a-f]{40}", chk) else None,
            checksum=chk if re.fullmatch(r"[0-9a-f]{40}", chk) else None,
            attrs={"category": cat},
        ))
    lic = project.get("license")
    return Listing(files=files, meta={
        "title": project.get("title", "").replace("\n", " ").strip(),
        "license": lic if isinstance(lic, str) else str(lic),
        "source_url": f"https://www.ebi.ac.uk/pride/archive/projects/{acc}",
        "citation": "; ".join(r.get("referenceLine", "") for r in project.get("references", []) if isinstance(r, dict)),
        "accession": acc,
    })
