"""Path guards: every write target must resolve inside an allowlisted root."""
from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from . import NasError
from .config import Config

_CTRL = re.compile(r"[\x00-\x1f\x7f]")


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_dest(cfg: Config, dest: str | None, default_rel: str | None = None) -> Path:
    """Resolve a user/agent-supplied destination. Relative paths are taken under omics_root.

    Resolution follows symlinks (strict=False), so a symlink pointing outside the
    allowlist is rejected just like '..' traversal.
    """
    raw = (dest or default_rel or "").strip()
    if not raw:
        raise NasError("No destination given and the dataset has no default nas_path.")
    if _CTRL.search(raw):
        raise NasError("Destination contains control characters.")
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = cfg.omics_root / p
    resolved = p.resolve(strict=False)
    roots = [r.resolve(strict=False) for r in cfg.allowed_roots]
    if not any(_within(resolved, r) for r in roots):
        raise NasError(
            f"Destination {resolved} is outside the allowed roots "
            f"({', '.join(map(str, roots))}). Pick a folder inside them (see nas_list_folders)."
        )
    return resolved


def safe_relpath(rel: str) -> PurePosixPath:
    """Sanitise a remote-supplied relative path (untrusted) into a safe POSIX relpath."""
    rel = _CTRL.sub("", rel.replace("\\", "/"))
    parts = [p for p in rel.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." for p in parts):
        raise NasError(f"Unsafe or empty relative path from source: {rel!r}")
    return PurePosixPath(*parts)


def ensure_inside(child: Path, parent: Path) -> Path:
    c = child.resolve(strict=False)
    if not _within(c, parent.resolve(strict=False)):
        raise NasError(f"Refusing to touch {c}: outside {parent}.")
    return c


def slug(text: str, max_len: int = 80) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._")
    return (s or "item")[:max_len]
