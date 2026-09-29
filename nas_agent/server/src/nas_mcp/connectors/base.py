from __future__ import annotations

import re
from dataclasses import dataclass, field

from .. import NasError
from ..manifest import FileEntry


@dataclass
class Listing:
    files: list[FileEntry] = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    kind: str = "aria2"
    command: list[str] | None = None


def require(params: dict, key: str, pattern: str | None = None, example: str = "") -> str:
    val = str(params.get(key) or "").strip()
    if not val:
        raise NasError(f"Missing parameter '{key}'" + (f" (e.g. {example})" if example else "") + ".")
    if pattern and not re.fullmatch(pattern, val):
        raise NasError(f"Parameter '{key}'={val!r} is not valid" + (f"; expected like {example}" if example else "") + ".")
    return val
