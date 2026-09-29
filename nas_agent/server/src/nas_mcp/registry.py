"""Dataset registry (datasets/registry.yaml) and the access-policy gate."""
from __future__ import annotations

import yaml

from . import NasError
from .config import Config

POLICIES = ("allowed", "summary_only", "check_dua", "forbidden")
ACK_REQUIRED = {"summary_only", "check_dua"}


def load(cfg: Config) -> dict[str, dict]:
    if not cfg.registry_path.is_file():
        raise NasError(f"Registry not found at {cfg.registry_path}; check 'registry' in config.yaml.")
    data = yaml.safe_load(cfg.registry_path.read_text()) or {}
    out = {}
    for d in data.get("datasets", []):
        if d.get("local_download") not in POLICIES:
            raise NasError(f"Registry entry {d.get('id')} has invalid local_download {d.get('local_download')!r}")
        out[d["id"]] = d
    return out


def get(cfg: Config, dataset_id: str) -> dict:
    reg = load(cfg)
    if dataset_id not in reg:
        close = [k for k in reg if dataset_id.lower().split("-")[0] in k]
        raise NasError(f"Unknown dataset_id {dataset_id!r}. "
                       + (f"Did you mean {close}? " if close else "")
                       + "Use nas_catalog_search to list registry ids.")
    return reg[dataset_id]


def search(cfg: Config, query: str = "") -> list[dict]:
    q = query.lower().split()
    rows = []
    for d in load(cfg).values():
        hay = " ".join(str(d.get(k, "")) for k in ("id", "name", "modality", "notes", "access", "keywords")).lower()
        if all(t in hay for t in q):
            rows.append({k: d.get(k) for k in ("id", "name", "modality", "local_download", "connector",
                                                "defaults", "nas_path", "notes", "verified", "docs")})
    return rows


def gate(entry: dict) -> None:
    """Refuse to plan anything the registry marks as non-downloadable."""
    pol, conn = entry["local_download"], entry.get("connector")
    if pol == "forbidden":
        raise NasError(
            f"{entry['name']}: participant-level data may not leave the provider's platform "
            f"({entry.get('access', '')}). Analyse it in the enclave and export only summary results. "
            "Nothing was queued."
        )
    if conn in (None, "none", "manual"):
        raise NasError(
            f"{entry['name']} has no automated connector (access: {entry.get('access', 'see docs')}). "
            + ("Download manually per your DUA, then use nas_verify on the folder."
               if conn == "manual" else "Use the provider's platform.")
        )


def merge_params(entry: dict, params: dict | None) -> dict:
    merged = dict(entry.get("defaults") or {})
    locked = set(entry.get("locked") or [])
    for k, v in (params or {}).items():
        if k in locked and k in merged and merged[k] != v:
            raise NasError(f"'{k}' is fixed to {merged[k]!r} for {entry['id']}.")
        merged[k] = v
    return merged


def check_ack(policy: str, ack: str | None) -> None:
    if policy in ACK_REQUIRED and not (ack and len(ack.strip()) >= 8):
        need = ("the DUA/DUC name or ID that permits storing this data on this personal NAS, "
                "and that the approval is personal (not employer-held)"
                if policy == "check_dua" else
                "confirmation that only summary statistics / metadata are being downloaded")
        raise NasError(f"Policy '{policy}' requires policy_ack: {need}. Ask the user; do not invent it.")
