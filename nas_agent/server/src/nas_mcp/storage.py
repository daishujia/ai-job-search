"""Read-mostly storage tools, restricted to the allowlisted roots."""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

from . import NasError
from .config import Config
from .manifest import human
from .paths import resolve_dest

SKIP_PREFIXES = (".", "@", "#recycle")


def overview(cfg: Config) -> dict:
    from .paths import to_client
    return {"database_root": str(cfg.omics_root),
            "database_root_client": to_client(cfg, cfg.omics_root) if cfg.client_root else None,
            "layout": "<database>/<SOURCE>/<PROJECT_CODE>/{raw,processed,metadata}",
            "volumes": _volumes(cfg)}


def _volumes(cfg: Config) -> list[dict]:
    seen, rows = set(), []
    candidates = list(cfg.allowed_roots) + sorted(Path("/").glob("vol*"))
    for root in candidates:
        p = root
        while not p.exists() and p != p.parent:
            p = p.parent
        try:
            dev = os.stat(p).st_dev
        except OSError:
            continue
        if dev in seen:
            continue
        seen.add(dev)
        du = shutil.disk_usage(p)
        rows.append({"path": str(root), "total": human(du.total), "used": human(du.used), "free": human(du.free),
                     "used_pct": round(100 * du.used / du.total, 1) if du.total else None,
                     "warning": "above 80% used" if du.total and du.used / du.total > 0.8 else ""})
    return rows


def list_folders(cfg: Config, path: str | None = None, depth: int = 1, max_entries: int = 300) -> dict:
    base = resolve_dest(cfg, path or str(cfg.omics_root))
    if not base.is_dir():
        raise NasError(f"{base} does not exist (create it with nas_create_folder).")
    depth = max(1, min(depth, 4))
    out: list[str] = []
    truncated = False
    for root, dirs, _ in os.walk(base):
        rel_depth = len(Path(root).relative_to(base).parts)
        dirs[:] = sorted(d for d in dirs if not d.startswith(SKIP_PREFIXES))
        if rel_depth >= depth:
            dirs[:] = []
            continue
        for d in dirs:
            out.append(str(Path(root, d).relative_to(base)) + "/")
            if len(out) >= max_entries:
                truncated = True
                break
        if truncated:
            break
    return {"base": str(base), "allowed_roots": [str(r) for r in cfg.allowed_roots],
            "folders": out, "truncated": truncated}


def folder_usage(cfg: Config, path: str, time_limit: float = 20.0) -> dict:
    base = resolve_dest(cfg, path)
    if not base.is_dir():
        raise NasError(f"{base} is not a directory.")
    t0, total, nfiles, per_child, truncated = time.time(), 0, 0, {}, False
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if not d.startswith(("@", "#recycle"))]
        rel = Path(root).relative_to(base).parts
        child = rel[0] if rel else "(files here)"
        for n in files:
            try:
                s = os.lstat(os.path.join(root, n)).st_size
            except OSError:
                continue
            total += s
            nfiles += 1
            per_child[child] = per_child.get(child, 0) + s
        if time.time() - t0 > time_limit:
            truncated = True
            break
    top = sorted(per_child.items(), key=lambda kv: kv[1], reverse=True)[:15]
    return {"path": str(base), "total": human(total), "files": nfiles, "truncated_after_s": time_limit if truncated else None,
            "largest_children": [{"name": k, "size": human(v)} for k, v in top]}


def create_folder(cfg: Config, path: str) -> dict:
    p = resolve_dest(cfg, path)
    existed = p.exists()
    p.mkdir(parents=True, exist_ok=True)
    return {"path": str(p), "created": not existed}
