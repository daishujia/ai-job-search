"""Build a Plan from a registry entry (+ connector params) without downloading anything."""
from __future__ import annotations

from . import NasError
from . import registry
from .config import Config
from .connectors import CONNECTORS, pdc, s3
from .http import Http
from .layout import LEVELS, classify, project_location
from .manifest import Plan, apply_filters, new_plan_id
from .paths import resolve_dest, safe_relpath


def plan_dataset(cfg: Config, dataset_id: str, params: dict | None, project_code: str | None = None,
                 source: str | None = None, levels: list[str] | None = None, include: list[str] | None = None,
                 exclude: list[str] | None = None, max_files: int | None = None, http: Http | None = None) -> Plan:
    entry = registry.get(cfg, dataset_id)
    registry.gate(entry)
    merged = registry.merge_params(entry, params)
    conn = entry["connector"]
    if conn not in CONNECTORS:
        raise NasError(f"Registry connector {conn!r} is not implemented.")
    bad = [lv for lv in levels or [] if lv not in LEVELS]
    if bad:
        raise NasError(f"levels must be among {LEVELS}; got {bad}")
    src, code, project_dir = project_location(cfg, entry, merged, project_code, source)
    target = resolve_dest(cfg, str(project_dir))  # validate before any network call
    listing = CONNECTORS[conn](merged, http or Http(), cfg)

    files = apply_filters(listing.files, include, exclude, None)
    kept = []
    for f in files:
        lv = classify(f, conn)
        if levels and lv not in levels and lv != "metadata":  # metadata files always come along
            continue
        f.relpath = f"{lv}/{safe_relpath(f.relpath)}"
        kept.append(f)
    kept = kept[:max_files] if max_files else kept
    if listing.kind == "aria2" and not kept:
        raise NasError(f"No files matched (listed {len(listing.files)} before filters). Loosen include/exclude/levels.")
    plan = Plan(plan_id=new_plan_id(), dataset_id=dataset_id, connector=conn, params=merged, dest=str(target),
                policy=entry["local_download"], files=kept, kind=listing.kind, command=listing.command,
                source=src, project_code=code, record=listing.record,
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


def plan_urls(cfg: Config, urls: list, source: str, project_code: str, levels: list[str] | None = None,
              http: Http | None = None) -> Plan:
    return plan_dataset(cfg, "open-urls", {"urls": urls}, project_code, source, levels, http=http)
