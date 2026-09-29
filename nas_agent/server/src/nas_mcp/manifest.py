"""File entries, plans (a resolved manifest awaiting confirmation) and their persistence."""
from __future__ import annotations

import fnmatch
import json
import secrets
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import NasError
from .config import Config

CHECKSUM_TYPES = {"md5", "sha-1", "sha-256"}


@dataclass
class FileEntry:
    url: str
    relpath: str
    size: int | None = None
    size_exact: bool = True            # False when the source's size is only indicative (PRIDE)
    checksum_type: str | None = None   # md5 | sha-1 | sha-256 (aria2 names)
    checksum: str | None = None
    auth: str | None = None            # symbolic credential name, e.g. "hf"; never the secret itself
    attrs: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.checksum_type and self.checksum_type not in CHECKSUM_TYPES:
            raise NasError(f"Unsupported checksum type {self.checksum_type}")


@dataclass
class Plan:
    plan_id: str
    dataset_id: str
    connector: str
    params: dict
    dest: str
    policy: str
    files: list[FileEntry] = field(default_factory=list)
    kind: str = "aria2"                # aria2 | process
    command: list[str] | None = None   # for kind=process
    meta: dict = field(default_factory=dict)  # title, license, source_url, citation, notes
    created: float = field(default_factory=time.time)

    # ---- persistence ----
    def save(self, cfg: Config) -> Path:
        path = cfg.plans_dir / f"{self.plan_id}.json"
        path.write_text(json.dumps(asdict(self)))
        return path

    @staticmethod
    def load(cfg: Config, plan_id: str) -> "Plan":
        if not plan_id.isalnum():
            raise NasError("Invalid plan_id.")
        path = cfg.plans_dir / f"{plan_id}.json"
        if not path.is_file():
            raise NasError(f"Unknown plan_id {plan_id}. Create one with nas_plan_dataset or nas_plan_urls.")
        d = json.loads(path.read_text())
        d["files"] = [FileEntry(**f) for f in d.get("files", [])]
        return Plan(**d)

    # ---- summaries ----
    @property
    def known_bytes(self) -> int:
        return sum(f.size or 0 for f in self.files)

    def summary(self, top: int = 10) -> dict:
        exts = Counter(Path(f.relpath).suffix.lower() or "(none)" for f in self.files)
        biggest = sorted(self.files, key=lambda f: f.size or 0, reverse=True)[:top]
        return {
            "plan_id": self.plan_id,
            "dataset_id": self.dataset_id,
            "policy": self.policy,
            "kind": self.kind,
            "dest": self.dest,
            "file_count": len(self.files),
            "total_bytes_known": self.known_bytes,
            "total_human": human(self.known_bytes),
            "files_without_size": sum(1 for f in self.files if f.size is None),
            "sizes_are_estimates": any(not f.size_exact for f in self.files),
            "with_checksum": sum(1 for f in self.files if f.checksum),
            "extensions": dict(exts.most_common(12)),
            "largest": [{"path": f.relpath, "size": human(f.size or 0)} for f in biggest],
            "meta": self.meta,
            "command": self.command,
        }


def new_plan_id() -> str:
    return time.strftime("%Y%m%d") + secrets.token_hex(4)


def apply_filters(files: list[FileEntry], include: list[str] | None, exclude: list[str] | None,
                  max_files: int | None) -> list[FileEntry]:
    """Glob filters match against the relpath and the basename (case-insensitive)."""
    def match(f: FileEntry, pats: list[str]) -> bool:
        rp, name = f.relpath.lower(), Path(f.relpath).name.lower()
        return any(fnmatch.fnmatch(rp, p.lower()) or fnmatch.fnmatch(name, p.lower()) for p in pats)

    out = [f for f in files if (not include or match(f, include)) and not (exclude and match(f, exclude))]
    seen: set[str] = set()
    uniq = []
    for f in out:  # duplicate relpaths would make aria2 clobber / rename files
        if f.relpath in seen:
            continue
        seen.add(f.relpath)
        uniq.append(f)
    return uniq[:max_files] if max_files else uniq


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} TB"
