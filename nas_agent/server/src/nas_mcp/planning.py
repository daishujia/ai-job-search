"""Build a Plan from a registry entry (+ connector params) without downloading anything."""
from __future__ import annotations

from pathlib import Path

from . import NasError
from . import registry
from .config import Config
from .connectors import CONNECTORS, pdc, s3
from .http import Http
from .manifest import Plan, apply_filters, new_plan_id
from .paths import resolve_dest, safe_relpath


def plan_dataset(cfg: Config, dataset_id: str, params: dict | None, dest: str | None,
                 include: list[str] | None, exclude: list[str] | None, max_files: int | None,
                 http: Http | None = None) -> Plan:
    entry = registry.get(cfg, dataset_id)
    registry.gate(entry)
    merged = registry.merge_params(entry, params)
    conn = entry["connector"]
    if conn not in CONNECTORS:
        raise NasError(f"Registry connector {conn!r} is not implemented.")
    default_rel = entry.get("nas_path", "").format_map(_Fmt(merged))
    if not dest and "{" in default_rel:
        raise NasError(f"Default folder {default_rel!r} needs a parameter that was not given; pass dest explicitly.")
    target = resolve_dest(cfg, dest, default_rel)  # validate before any network call
    listing = CONNECTORS[conn](merged, http or Http(), cfg)
    files = apply_filters(listing.files, include, exclude, max_files)
    for f in files:
        f.relpath = str(safe_relpath(f.relpath))
    if listing.kind == "aria2" and not files:
        raise NasError(f"No files matched (listed {len(listing.files)} before filters). Loosen include/exclude.")
    plan = Plan(plan_id=new_plan_id(), dataset_id=dataset_id, connector=conn, params=merged, dest=str(target),
                policy=entry["local_download"], files=files, kind=listing.kind, command=listing.command,
                meta={**{k: entry.get(k) for k in ("name", "docs")}, **listing.meta,
                      "listed_before_filters": len(listing.files)})
    plan.save(cfg)
    return plan


def browse(cfg: Config, dataset_id: str, params: dict | None, http: Http | None = None) -> dict:
    """Lightweight look inside a source before planning (S3 sub-folders, PDC data categories)."""
    entry = registry.get(cfg, dataset_id)
    registry.gate(entry)
    merged = registry.merge_params(entry, params)
    http = http or Http()
    if entry["connector"] == "s3":
        prefix = str(merged.get("prefix") or "")
        subs = s3.list_prefixes(http, merged["bucket"], merged.get("region", "us-east-1"), prefix)
        return {"bucket": merged["bucket"], "prefix": prefix, "subfolders": subs[:500],
                "hint": "Pass one of these as params.prefix to nas_plan_dataset (or browse deeper)."}
    if entry["connector"] == "pdc":
        try:
            pdc.list_files({**merged, "data_categories": []}, http, cfg)
        except NasError as e:  # the category overview is delivered as a guidance message
            return {"categories": str(e)}
    raise NasError("Browsing is available for s3 and pdc sources; for others run nas_plan_dataset "
                   "(it lists without downloading).")


class _Fmt(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def plan_urls(cfg: Config, urls: list, dest: str, http: Http | None = None) -> Plan:
    plan = plan_dataset(cfg, "open-urls", {"urls": urls}, dest, None, None, None, http)
    return plan
