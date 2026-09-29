"""MassIVE (MSV accessions): PROXI API for the FTP location, then an FTP walk.

aria2 downloads ftp:// URLs directly. Not live-tested from the build environment (no FTP egress).
"""
from __future__ import annotations

import ftplib
from urllib.parse import quote, urlparse

from .. import NasError
from ..manifest import FileEntry
from .base import Listing, require

PROXI = "https://massive.ucsd.edu/ProteoSAFe/proxi/v0.1/datasets"


def _walk(ftp: ftplib.FTP, path: str, rel: str, out: list, cap: int, depth: int = 0) -> None:
    if depth > 8:
        return
    try:
        entries = list(ftp.mlsd(path, facts=["type", "size"]))
    except ftplib.error_perm:  # server without MLSD: probe each NLST entry
        entries = []
        for full_name in ftp.nlst(path):
            name = full_name.rstrip("/").rsplit("/", 1)[-1]
            try:
                size = ftp.size(f"{path.rstrip('/')}/{name}")
                entries.append((name, {"type": "file", "size": str(size) if size is not None else ""}))
            except ftplib.error_perm:
                entries.append((name, {"type": "dir"}))
    for name, facts in entries:
        if name in (".", ".."):
            continue
        full, r = f"{path.rstrip('/')}/{name}", f"{rel}{name}"
        if facts.get("type") == "dir":
            _walk(ftp, full, r + "/", out, cap, depth + 1)
        elif facts.get("type") == "file":
            out.append((full, r, int(facts["size"]) if facts.get("size") else None))
            if len(out) >= cap:
                raise NasError(f"MassIVE listing exceeds {cap} files; add include filters or a 'subdir'.")


def list_files(params: dict, http, cfg, ftp_factory=ftplib.FTP) -> Listing:
    acc = require(params, "accession", r"MSV\d{9}", "MSV000079514")
    d = http.get_json(f"{PROXI}/{acc}")
    loc = next((l.get("value") for l in d.get("datasetLink", []) if "FTP" in (l.get("name") or "")), None)
    if not loc:
        raise NasError(f"No FTP location published for {acc}.")
    u = urlparse(loc)
    base = u.path.rstrip("/") + ("/" + params["subdir"].strip("/") if params.get("subdir") else "")
    found: list = []
    ftp = ftp_factory(u.hostname, timeout=60)
    try:
        ftp.login()
        _walk(ftp, base, "", found, int(params.get("max_files") or cfg.max_plan_files))
    finally:
        try:
            ftp.quit()
        except Exception:
            pass
    files = [FileEntry(url=f"ftp://{u.hostname}{quote(p)}", relpath=r, size=s) for p, r, s in found]
    return Listing(files=files, record=d, meta={"title": d.get("title"), "accession": acc,
                                      "source_url": f"https://massive.ucsd.edu/ProteoSAFe/QueryMSV?id={acc}"})
