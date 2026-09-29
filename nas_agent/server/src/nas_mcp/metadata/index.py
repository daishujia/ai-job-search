"""SQLite index over every <SOURCE>/<PROJECT>/metadata/study.json (+ drafts), and CATALOG.tsv.

Lives in <database root>/_catalog/ so it travels with the data (visible on the Mac too).
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from ..config import Config
from ..manifest import human
from ..paths import to_client

TERM_FIELDS = ("organism", "tissue", "sample_type", "cell_type", "cell_line", "disease", "sex")

DDL = """
CREATE TABLE IF NOT EXISTS studies (
  source TEXT, project_code TEXT, title TEXT, modality TEXT, status TEXT, registry_id TEXT,
  n_subjects INTEGER, n_samples INTEGER, n_cells INTEGER, raw_bytes INTEGER, processed_bytes INTEGER,
  path TEXT, client_path TEXT, license TEXT, access_policy TEXT, doi TEXT, updated TEXT, study_json TEXT,
  PRIMARY KEY (source, project_code));
CREATE TABLE IF NOT EXISTS terms (
  source TEXT, project_code TEXT, field TEXT, label TEXT, term_id TEXT);
CREATE INDEX IF NOT EXISTS terms_idx ON terms(field, label, term_id);
"""


def _db(cfg: Config) -> sqlite3.Connection:
    cfg.catalog_dir.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(cfg.catalog_dir / "catalog.sqlite")
    con.executescript(DDL)
    return con


def upsert(cfg: Config, st: dict) -> None:
    idn, des, data = st["identity"], st.get("design", {}), st.get("data", {})
    lv = data.get("levels", {})
    key = (idn["source"], idn["project_code"])
    with _db(cfg) as con:
        con.execute("DELETE FROM terms WHERE source=? AND project_code=?", key)
        con.execute("INSERT OR REPLACE INTO studies VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            *key, idn.get("title"), ",".join(st["assay"].get("modality", [])), st["curation"]["status"],
            idn.get("registry_id"), des.get("n_subjects"), des.get("n_samples"), des.get("n_cells"),
            lv.get("raw", {}).get("bytes"), lv.get("processed", {}).get("bytes"), data.get("nas_path"),
            data.get("client_path"), idn.get("license"), idn.get("access_policy"), idn.get("doi"),
            time.strftime("%Y-%m-%dT%H:%M:%S"), json.dumps(st)))
        rows = [(*key, f, t.get("label"), t.get("id")) for f in TERM_FIELDS for t in st.get("biology", {}).get(f, [])]
        rows += [(*key, "technology", t.get("label"), t.get("id")) for t in st["assay"].get("technology", [])]
        con.executemany("INSERT INTO terms VALUES (?,?,?,?,?)", rows)
    write_catalog_tsv(cfg)


def _first(con, key, field) -> str:
    r = con.execute("SELECT group_concat(label, '; ') FROM (SELECT label FROM terms WHERE source=? AND project_code=? "
                    "AND field=? LIMIT 4)", (*key, field)).fetchone()
    return r[0] or ""


def write_catalog_tsv(cfg: Config) -> Path:
    out = cfg.omics_root / "CATALOG.tsv"
    with _db(cfg) as con:
        rows = con.execute("SELECT source, project_code, title, modality, status, n_samples, n_cells, raw_bytes, "
                           "processed_bytes, license, access_policy, client_path, path FROM studies "
                           "ORDER BY source, project_code").fetchall()
        lines = ["source\tproject_code\ttitle\tmodality\torganism\tdisease\ttissue_or_sample\tn_samples\tn_cells\t"
                 "raw_size\tprocessed_size\tlicense\taccess_policy\tmetadata_status\tpath"]
        for (src, code, title, mod, status, ns, nc, rb, pb, lic, pol, cpath, path) in rows:
            key = (src, code)
            tissue = _first(con, key, "tissue") or _first(con, key, "sample_type")
            lines.append("\t".join(str(x if x is not None else "") for x in (
                src, code, (title or "").replace("\t", " ")[:150], mod, _first(con, key, "organism"),
                _first(con, key, "disease"), tissue, ns, nc, human(rb or 0) if rb else "", human(pb or 0) if pb else "",
                lic, pol, status, cpath or path)))
    out.write_text("\n".join(lines) + "\n")
    return out


def query(cfg: Config, text: str = "", filters: dict | None = None, limit: int = 50) -> list[dict]:
    filters = {k: v for k, v in (filters or {}).items() if v}
    sql = "SELECT s.source, s.project_code, s.title, s.modality, s.status, s.n_samples, s.n_cells, s.raw_bytes, " \
          "s.processed_bytes, s.client_path, s.path FROM studies s WHERE 1=1"
    args: list = []
    for field in ("source", "status"):
        if field in filters:
            sql += f" AND lower(s.{field}) = lower(?)"
            args.append(filters.pop(field))
    if "modality" in filters:
        sql += " AND lower(s.modality) LIKE lower(?)"
        args.append(f"%{filters.pop('modality')}%")
    for field, val in filters.items():
        sql += (" AND EXISTS (SELECT 1 FROM terms t WHERE t.source=s.source AND t.project_code=s.project_code "
                "AND t.field=? AND (lower(t.label) LIKE lower(?) OR t.term_id = ?))")
        args += [field, f"%{val}%", val]
    for word in text.split():
        sql += " AND lower(s.study_json) LIKE lower(?)"
        args.append(f"%{word}%")
    sql += " ORDER BY s.source, s.project_code LIMIT ?"
    args.append(limit)
    with _db(cfg) as con:
        rows = con.execute(sql, args).fetchall()
    cols = ["source", "project_code", "title", "modality", "metadata_status", "n_samples", "n_cells", "raw_bytes",
            "processed_bytes", "client_path", "path"]
    out = []
    for r in rows:
        d = dict(zip(cols, r))
        d["raw_size"] = human(d.pop("raw_bytes") or 0)
        d["processed_size"] = human(d.pop("processed_bytes") or 0)
        out.append(d)
    return out


def rebuild(cfg: Config) -> dict:
    n, errors = 0, []
    with _db(cfg) as con:
        con.execute("DELETE FROM studies")
        con.execute("DELETE FROM terms")
    for meta in sorted(cfg.omics_root.glob("*/*/metadata")):
        for name in ("study.json", "study.draft.json"):
            p = meta / name
            if p.is_file():
                try:
                    st = json.loads(p.read_text())
                    st.setdefault("data", {})["client_path"] = to_client(cfg, meta.parent) if cfg.client_root else None
                    upsert(cfg, st)
                    n += 1
                except Exception as e:
                    errors.append(f"{p}: {e}")
                break  # curated study.json wins over the draft
    write_catalog_tsv(cfg)
    return {"indexed": n, "errors": errors[:20]}
