"""Hugging Face Hub datasets/models (e.g. tahoebio/Tahoe-100M)."""
from __future__ import annotations

from urllib.parse import quote

from .. import NasError
from ..manifest import FileEntry
from .base import Listing, require

HUB = "https://huggingface.co"


def list_files(params: dict, http, cfg) -> Listing:
    repo = require(params, "repo", r"[\w.\-]+/[\w.\-]+", "tahoebio/Tahoe-100M")
    rtype = params.get("repo_type", "dataset")
    if rtype not in ("dataset", "model"):
        raise NasError("repo_type must be 'dataset' or 'model'.")
    api = f"{HUB}/api/{rtype}s/{repo}"
    web = f"{HUB}/datasets/{repo}" if rtype == "dataset" else f"{HUB}/{repo}"
    headers = {"Authorization": f"Bearer {cfg.hf_token}"} if cfg.hf_token else None
    info = http.get_json(api, headers=headers)
    sha = params.get("revision") or info.get("sha")
    path = str(params.get("path") or "").strip("/")
    tree_url = f"{api}/tree/{sha}" + (f"/{quote(path)}" if path else "")
    entries = http.get_json_paged(tree_url, params={"recursive": "true"}, headers=headers)
    gated = bool(info.get("gated"))
    if gated and not cfg.hf_token:
        raise NasError(f"{repo} is gated: accept its terms on huggingface.co and put a read token in "
                       "the NAS token file (tokens.huggingface_file in config.yaml).")
    files = []
    for e in entries:
        if e.get("type") != "file":
            continue
        lfs = e.get("lfs") or {}
        files.append(FileEntry(
            url=f"{web}/resolve/{sha}/{quote(e['path'])}",
            relpath=e["path"], size=e.get("size"),
            checksum_type="sha-256" if lfs.get("oid") else None, checksum=lfs.get("oid"),
            auth="hf" if gated else None,
        ))
    card = info.get("cardData") or {}
    record = {k: v for k, v in info.items() if k not in ("siblings",)}
    return Listing(files=files, record=record, meta={
        "title": repo, "revision": sha, "license": card.get("license"),
        "source_url": f"{web}/tree/{sha}", "gated": gated,
    })
