"""Plain URL lists (HPA, HCA manifests, DepMap release files, anything direct-download)."""
from __future__ import annotations

import re
from urllib.parse import unquote, urlparse

from .. import NasError
from ..manifest import FileEntry
from .base import Listing

SCHEMES = {"http", "https", "ftp", "sftp"}


def list_files(params: dict, http, cfg) -> Listing:
    items = params.get("urls") or []
    if not items:
        raise NasError("params.urls is empty. Pass a list of URLs or {url, name?, md5?|sha256?} objects.")
    files = []
    for it in items:
        it = {"url": it} if isinstance(it, str) else dict(it)
        u = urlparse(it["url"])
        if u.scheme not in SCHEMES or not u.netloc:
            raise NasError(f"Unsupported URL {it['url']!r}: only {sorted(SCHEMES)} are allowed.")
        name = it.get("name") or unquote(u.path.rstrip("/").rsplit("/", 1)[-1]) or "download"
        ctype, digest = None, None
        for key, t, n in (("md5", "md5", 32), ("sha1", "sha-1", 40), ("sha256", "sha-256", 64)):
            v = (it.get(key) or "").lower()
            if v:
                if not re.fullmatch(rf"[0-9a-f]{{{n}}}", v):
                    raise NasError(f"Bad {key} for {name}")
                ctype, digest = t, v
        files.append(FileEntry(url=it["url"], relpath=name, size=it.get("size"),
                               checksum_type=ctype, checksum=digest))
    return Listing(files=files, meta={"source_url": "user-supplied URL list"})
