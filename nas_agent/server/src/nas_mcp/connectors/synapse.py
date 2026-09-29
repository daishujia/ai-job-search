"""Synapse (AD Knowledge Portal, UKB-PPP summary stats) via the `synapse` CLI as a background job.

Synapse issues short-lived presigned URLs per file, so the synapseclient CLI does the transfer
itself. Auth is the user's own: a personal access token in ~/.synapseConfig on the NAS
(or SYNAPSE_AUTH_TOKEN). Sizes are not known up front; preflight only enforces the reserve.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from .. import NasError
from .base import Listing, require


def list_files(params: dict, http, cfg) -> Listing:
    syn = require(params, "syn_id", r"syn\d{3,12}", "syn51365301")
    exe = shutil.which("synapse") or str(Path(__import__("sys").executable).parent / "synapse")
    if not Path(exe).exists():
        raise NasError("synapseclient is not installed in the nas-mcp venv. On the NAS run: "
                       "~/nas-mcp/.venv/bin/pip install 'synapseclient>=4'")
    if not (Path("~/.synapseConfig").expanduser().is_file() or __import__("os").environ.get("SYNAPSE_AUTH_TOKEN")):
        raise NasError("No Synapse credentials on the NAS. Create a personal access token at synapse.org "
                       "and run `synapse config` as the agent user (the token stays on the NAS).")
    return Listing(kind="process", command=[exe, "get", "-r", syn, "--downloadLocation", "{dest}/_incoming"],
                   record={"syn_id": syn},
                   meta={"source_url": f"https://www.synapse.org/Synapse:{syn}", "accession": syn})
