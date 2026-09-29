"""Structural peeks into downloaded files so metadata can be extracted from content, not just APIs.

Cheap by design: headers, first rows, SDRF characteristics, h5ad obs columns, mzTab MTD lines,
parquet schema, zip listings. Raw instrument files are only counted.
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import zipfile
from collections import Counter
from pathlib import Path

from ..layout import LEVELS, _ext

TABLE_EXT = {".tsv", ".csv", ".txt", ".tab"}
MAX_UNIQUES = 12


def _open_text(p: Path):
    if p.name.lower().endswith(".gz"):
        return io.TextIOWrapper(gzip.open(p, "rb"), encoding="utf-8", errors="replace")
    return open(p, encoding="utf-8", errors="replace")


def _sniff_delim(line: str) -> str:
    return "\t" if line.count("\t") >= line.count(",") else ","


def inspect_table(p: Path, max_rows: int = 200_000) -> dict:
    with _open_text(p) as fh:
        first = fh.readline()
        if not first:
            return {"kind": "table", "empty": True}
        delim = _sniff_delim(first)
        header = next(csv.reader([first], delimiter=delim))
        rows, uniques = 0, {h: Counter() for h in header[:200]}
        sample = []
        for rec in csv.reader(fh, delimiter=delim):
            rows += 1
            if len(sample) < 3:
                sample.append([c[:40] for c in rec[:12]])
            if rows <= 5000:
                for h, v in zip(header[:200], rec):
                    if len(uniques[h]) <= 50:
                        uniques[h][v] += 1
            if rows >= max_rows:
                break
    low_card = {h: [v for v, _ in c.most_common(MAX_UNIQUES)] for h, c in uniques.items() if 0 < len(c) <= 50}
    return {"kind": "table", "delimiter": "tab" if delim == "\t" else "comma", "n_columns": len(header),
            "columns": header[:80], "n_rows_scanned": rows, "row_count_capped": rows >= max_rows,
            "first_rows": sample, "categorical_columns": dict(list(low_card.items())[:40])}


def inspect_sdrf(p: Path) -> dict:
    t = inspect_table(p)
    t["kind"] = "sdrf"
    t["characteristics"] = {k: v for k, v in t.get("categorical_columns", {}).items()
                            if k.lower().startswith(("characteristics", "factor value", "comment[label", "comment[instrument"))}
    return t


def read_sdrf_samples(p: Path) -> list[dict]:
    """Map SDRF-Proteomics rows to the standard samples columns (+ char:/comment: extras)."""
    with _open_text(p) as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    std_map = {
        "source name": "sample_id", "characteristics[organism]": "organism",
        "characteristics[organism part]": "tissue", "characteristics[disease]": "disease",
        "characteristics[sex]": "sex", "characteristics[age]": "age", "characteristics[cell type]": "cell_type",
        "characteristics[cell line]": "cell_line", "characteristics[developmental stage]": "development_stage",
        "characteristics[individual]": "subject_id", "characteristics[biological replicate]": "replicate",
        "comment[label]": "label", "comment[data file]": "data_file", "characteristics[material type]": "sample_type",
        "characteristics[treatment]": "treatment", "characteristics[compound]": "treatment",
    }
    out = []
    for r in rows:
        row: dict = {}
        for k, v in r.items():
            if k is None:
                continue
            kl = k.strip().lower()
            if kl in std_map and not row.get(std_map[kl]):
                row[std_map[kl]] = v
            elif kl.startswith("factor value[") and not row.get("condition"):
                row["condition"] = v
            elif kl.startswith("characteristics["):
                row[f"char:{k[16:-1]}"] = v
            elif kl.startswith("comment["):
                row[f"comment:{k[8:-1]}"] = v
        out.append(row)
    return out


def inspect_h5ad(p: Path) -> dict:
    try:
        import h5py  # optional dependency ([inspect] extra)
    except ImportError:
        return {"kind": "h5ad", "note": "install h5py in the nas-mcp venv for AnnData inspection (pip install h5py)"}
    info: dict = {"kind": "h5ad"}
    with h5py.File(p, "r") as f:
        obs = f.get("obs")
        var = f.get("var")

        def n_rows(group):
            if group is None:
                return None
            idx = group.attrs.get("_index", "_index")
            return len(group[idx]) if idx in group else None

        info["n_obs"], info["n_vars"] = n_rows(obs), n_rows(var)
        cats: dict = {}
        if obs is not None:
            info["obs_columns"] = [k for k in obs.keys() if k not in ("_index", "__categories")][:120]
            for k in info["obs_columns"]:
                node = obs[k]
                if isinstance(node, h5py.Group) and "categories" in node:
                    vals = [x.decode() if isinstance(x, bytes) else str(x) for x in node["categories"][:MAX_UNIQUES + 1]]
                    cats[k] = vals[:MAX_UNIQUES] + (["..."] if len(vals) > MAX_UNIQUES else [])
        info["obs_categories"] = cats
        info["uns_keys"] = list(f["uns"].keys())[:60] if "uns" in f else []
        if "uns" in f and "schema_version" in f["uns"]:
            v = f["uns"]["schema_version"][()]
            info["cellxgene_schema_version"] = v.decode() if isinstance(v, bytes) else str(v)
    return info


def inspect_parquet(p: Path) -> dict:
    try:
        import pyarrow.parquet as pq
    except ImportError:
        return {"kind": "parquet", "note": "install pyarrow for parquet inspection"}
    pf = pq.ParquetFile(p)
    return {"kind": "parquet", "n_rows": pf.metadata.num_rows, "columns": pf.schema_arrow.names[:120]}


def inspect_mztab(p: Path) -> dict:
    mtd = {}
    with _open_text(p) as fh:
        for i, line in enumerate(fh):
            if line.startswith("MTD"):
                parts = line.rstrip("\n").split("\t")
                if len(parts) >= 3 and len(mtd) < 150:
                    mtd[parts[1]] = parts[2][:200]
            elif i > 5000 or line[:3] in ("PRH", "PEH", "PSH", "SMH"):
                break
    return {"kind": "mztab", "metadata": mtd}


def inspect_zip(p: Path) -> dict:
    with zipfile.ZipFile(p) as z:
        names = z.namelist()
    return {"kind": "zip", "n_entries": len(names), "entries": names[:60]}


def inspect_json(p: Path) -> dict:
    if p.stat().st_size > 20 * 1024**2:
        return {"kind": "json", "note": "too large to inspect"}
    d = json.loads(p.read_text(errors="replace"))
    return {"kind": "json", "top_level": list(d)[:60] if isinstance(d, dict) else f"list[{len(d)}]"}


def inspect_file(p: Path) -> dict:
    name = p.name.lower()
    ext = _ext(name)
    try:
        if "sdrf" in name and ext in TABLE_EXT:
            return inspect_sdrf(p)
        if ext in (".mztab",):
            return inspect_mztab(p)
        if ext in TABLE_EXT:
            return inspect_table(p)
        if ext == ".h5ad":
            return inspect_h5ad(p)
        if ext == ".parquet":
            return inspect_parquet(p)
        if name.endswith(".zip"):
            return inspect_zip(p)
        if ext == ".json":
            return inspect_json(p)
    except Exception as e:  # a malformed file must not break the whole inspection
        return {"kind": "error", "error": f"{type(e).__name__}: {e}"[:300]}
    return {"kind": "unsupported", "ext": ext}


def inventory(project: Path) -> dict:
    """Counts/bytes/formats per level (raw/processed/metadata) from what is on disk."""
    out = {}
    for lv in LEVELS:
        base = project / lv
        files, total, fmts = 0, 0, Counter()
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file() and not p.name.endswith(".aria2"):
                    files += 1
                    total += p.stat().st_size
                    fmts[_ext(p.name) or "(none)"] += 1
        out[lv] = {"files": files, "bytes": total, "formats": [f for f, _ in fmts.most_common(10)]}
    return out


def inspect_project(project: Path, max_files: int = 30, levels=("metadata", "processed")) -> list[dict]:
    results = []
    for lv in levels:
        base = project / lv
        if not base.is_dir():
            continue
        files = sorted((p for p in base.rglob("*") if p.is_file() and not p.name.endswith(".aria2")
                        and "source" not in p.relative_to(base).parts[:1]),
                       key=lambda p: (0 if "sdrf" in p.name.lower() else 1, p.stat().st_size))
        for p in files:
            if len(results) >= max_files:
                return results
            results.append({"path": str(p.relative_to(project)), "size": p.stat().st_size, **inspect_file(p)})
    return results
