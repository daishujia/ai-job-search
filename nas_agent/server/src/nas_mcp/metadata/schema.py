"""Load/validate the ADMS study schema and read/write the standard samples table."""
from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

HERE = Path(__file__).parent
SCHEMA_VERSION = "1.0"


@lru_cache(maxsize=1)
def schema() -> dict:
    return json.loads((HERE / "study.schema.json").read_text())


@lru_cache(maxsize=1)
def sample_columns() -> list[str]:
    return [c["name"] for c in yaml.safe_load((HERE / "samples_columns.yaml").read_text())["columns"]]


def validate(study: dict) -> list[str]:
    v = Draft202012Validator(schema())
    errs = sorted(v.iter_errors(study), key=lambda e: list(e.absolute_path))
    return [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}" for e in errs][:50]


def normalise_sample_rows(rows: list[dict]) -> tuple[list[str], list[dict]]:
    """Standard columns first (in order); any other key becomes a char:/comment: column."""
    std = sample_columns()
    extra: list[str] = []
    out = []
    for r in rows:
        row = {}
        for k, v in r.items():
            key = k if k in std or k.startswith(("char:", "comment:")) else f"char:{k}"
            if key not in std and key not in extra:
                extra.append(key)
            row[key] = "" if v is None else str(v).replace("\t", " ").replace("\n", " ")
        out.append(row)
    used_std = [c for c in std if any(r.get(c) for r in out)] or ["sample_id"]
    if "sample_id" not in used_std:
        used_std.insert(0, "sample_id")
    return used_std + extra, out


def write_samples(path: Path, rows: list[dict]) -> int:
    cols, norm = normalise_sample_rows(rows)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(norm)
    return len(norm)


def read_samples(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))
