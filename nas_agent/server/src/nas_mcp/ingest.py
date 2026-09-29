"""Ingest data that is already on the NAS (manual downloads such as ADNI/LONI exports, older folders,
your own processed results) into <database>/<SOURCE>/<PROJECT>/{raw,processed,metadata}.

Two steps like downloads: plan (dry run, nothing touched) -> apply (after the user confirms).
mode=move renames within the same filesystem (instant, no extra space); mode=copy duplicates files.
Existing targets are never overwritten.
"""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

from . import NasError, registry
from .config import Config
from .layout import RESERVED, classify
from .manifest import FileEntry, human, new_plan_id
from .paths import component, ensure_inside, resolve_dest, to_client


def plan_ingest(cfg: Config, path: str, source: str, project_code: str, mode: str = "move",
                dataset_id: str | None = None, level: str | None = None, max_files: int = 200_000) -> dict:
    if mode not in ("move", "copy"):
        raise NasError("mode must be 'move' or 'copy'.")
    if level and level not in ("raw", "processed", "metadata"):
        raise NasError("level must be raw, processed or metadata (or omit it to auto-classify).")
    src_dir = resolve_dest(cfg, path)
    if not src_dir.exists():
        raise NasError(f"{src_dir} does not exist.")
    policy = "user_declared"
    if dataset_id:
        entry = registry.get(cfg, dataset_id)
        if entry["local_download"] == "forbidden":
            registry.gate(entry)  # raises with the enclave explanation
        policy = entry["local_download"]
    src_name, code = component(source, "source folder"), component(project_code, "project code")
    if src_name in RESERVED:
        raise NasError(f"{src_name} is reserved.")
    project = cfg.omics_root / src_name / code
    root_resolved = cfg.omics_root.resolve()
    if src_dir.resolve() == root_resolved or root_resolved in src_dir.resolve().parents and \
            len(src_dir.resolve().relative_to(root_resolved).parts) <= 2:
        raise NasError("That folder is already a database source/project folder; pick the folder that holds the files.")
    files = [src_dir] if src_dir.is_file() else sorted(p for p in src_dir.rglob("*") if p.is_file())
    items, conflicts, total = [], [], 0
    for p in files[:max_files]:
        rel = p.name if src_dir.is_file() else p.relative_to(src_dir).as_posix()
        lv = level or classify(FileEntry(url="", relpath=rel))
        target = ensure_inside(project / lv / rel, project)
        size = p.stat().st_size
        total += size
        (conflicts if target.exists() else items).append({"src": str(p), "dst": str(target), "level": lv, "size": size})
    if not items and not conflicts:
        raise NasError(f"No files found under {src_dir}.")
    same_fs = os.stat(src_dir).st_dev == os.stat(cfg.omics_root if cfg.omics_root.exists() else cfg.omics_root.parent).st_dev
    ingest_id = new_plan_id()
    plan = {"ingest_id": ingest_id, "mode": mode, "source": src_name, "project_code": code, "project": str(project),
            "dataset_id": dataset_id, "policy": policy, "from": str(src_dir), "items": items, "conflicts": conflicts,
            "created": time.time()}
    (cfg.ingests_dir / f"{ingest_id}.json").write_text(json.dumps(plan))
    by_level: dict = {}
    for it in items:
        b = by_level.setdefault(it["level"], {"files": 0, "bytes": 0})
        b["files"] += 1
        b["bytes"] += it["size"]
    return {"ingest_id": ingest_id, "mode": mode, "from": str(src_dir), "to": str(project),
            "to_client": to_client(cfg, project) if cfg.client_root else None,
            "files": len(items), "total": human(sum(i["size"] for i in items)),
            "by_level": {k: {"files": v["files"], "size": human(v["bytes"])} for k, v in by_level.items()},
            "existing_targets_skipped": len(conflicts), "same_filesystem": same_fs,
            "policy": policy, "truncated_at": max_files if len(files) > max_files else None,
            "note": ("move is an instant rename" if same_fs else
                     "different filesystem: use mode=copy (move across filesystems is not done automatically)"),
            "examples": [{"src": i["src"], "dst": i["dst"]} for i in items[:5]]}


def apply_ingest(cfg: Config, ingest_id: str, confirm: bool, policy_ack: str | None = None) -> dict:
    if not ingest_id.isalnum():
        raise NasError("Invalid ingest_id.")
    pf = cfg.ingests_dir / f"{ingest_id}.json"
    if not pf.is_file():
        raise NasError(f"Unknown ingest_id {ingest_id}; run nas_plan_ingest_local first.")
    plan = json.loads(pf.read_text())
    if plan.get("applied"):
        raise NasError("This ingest was already applied.")
    if not confirm:
        raise NasError("Show the user the ingest plan (files, sizes, from -> to, mode) and call again with confirm=true.")
    registry.check_ack(plan["policy"], policy_ack)
    project = Path(plan["project"])
    done, skipped, failed = 0, 0, []
    for it in plan["items"]:
        src, dst = Path(it["src"]), Path(it["dst"])
        if dst.exists():
            skipped += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            if plan["mode"] == "move":
                os.rename(src, dst)  # same filesystem only; raises EXDEV otherwise
            else:
                shutil.copy2(src, dst)
                if dst.stat().st_size != src.stat().st_size:
                    raise OSError("size mismatch after copy")
            done += 1
        except OSError as e:
            failed.append({"src": str(src), "error": str(e)[:200]})
            if plan["mode"] == "move" and getattr(e, "errno", None) == 18:
                failed[-1]["hint"] = "Cross-filesystem move: re-plan with mode=copy."
                break
    meta = project / "metadata" / "source"
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "_plan.json").write_text(json.dumps({"dataset_id": plan.get("dataset_id"), "connector": "local",
                                                 "policy": plan["policy"], "policy_ack": policy_ack,
                                                 "meta": {"title": f"{plan['source']} {plan['project_code']}",
                                                          "source_url": f"local ingest from {plan['from']}"},
                                                 "ingest_id": ingest_id, "submitted": time.time()}))
    _write_files_tsv(project)
    plan["applied"] = time.time()
    pf.write_text(json.dumps(plan))
    out = {"ingest_id": ingest_id, "project": str(project), "transferred": done, "skipped_existing": skipped,
           "failed": failed[:20]}
    if done:
        from .metadata.service import extract_draft
        try:
            r = extract_draft(cfg, project)
            out.update(metadata_draft=r["draft"], metadata_gaps=r["gaps"], samples_rows=r["samples_rows"])
        except Exception as e:  # noqa: BLE001
            out["metadata_error"] = str(e)[:300]
    return out


def _write_files_tsv(project: Path) -> None:
    with open(project / "files.tsv", "w") as fh:
        fh.write("relpath\tbytes\tchecksum_type\tchecksum\tverification\tsource_url\n")
        for p in sorted(project.rglob("*")):
            if p.is_file() and p.name not in ("files.tsv", "PROVENANCE.md") and "source" not in p.parts[-3:-1]:
                fh.write(f"{p.relative_to(project).as_posix()}\t{p.stat().st_size}\t\t\tlocal-ingest\t\n")
