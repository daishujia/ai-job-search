"""Project-level metadata operations used by the MCP tools and by post-download verification."""
from __future__ import annotations

import json
import time
from pathlib import Path

from .. import NasError, registry
from ..config import Config
from ..http import Http
from ..layout import resolve_project
from . import extract, index, inspect as insp, ontology, schema


def _meta_dir(project: Path) -> Path:
    d = project / "metadata"
    d.mkdir(exist_ok=True)
    return d


def _entry(cfg: Config, registry_id: str | None) -> dict | None:
    if not registry_id:
        return None
    try:
        return registry.get(cfg, registry_id)
    except NasError:
        return None


def fetch_extra(cfg: Config, project: Path, connector: str | None, record: dict | None, http: Http | None) -> None:
    """Source-side sample records worth keeping next to the data (PDC biospecimens)."""
    if connector != "pdc" or not record:
        return
    target = project / "metadata" / "source" / "biospecimens.json"
    if target.exists():
        return
    pid = record.get("study", {}).get("pdc_study_id")
    if not pid:
        return
    d = (http or Http()).post_json("https://pdc.cancer.gov/graphql", {"query":
        f'{{ biospecimenPerStudy(pdc_study_id: "{pid}", acceptDUA: true) {{ aliquot_id sample_id case_id '
        'aliquot_submitter_id sample_submitter_id case_submitter_id sample_type disease_type primary_site pool taxon } }'})
    rows = (d.get("data") or {}).get("biospecimenPerStudy") or []
    target.write_text(json.dumps(rows))


def extract_draft(cfg: Config, project_ref: str | Path, http: Http | None = None, online: bool = True) -> dict:
    project = resolve_project(cfg, str(project_ref))
    meta = _meta_dir(project)
    prov = {}
    pj = meta / "source" / "_plan.json"
    if pj.exists():
        prov = json.loads(pj.read_text())
    connector, record, bios = extract.load_records(project)
    if online and connector == "pdc" and bios is None:
        try:
            fetch_extra(cfg, project, connector, record, http)
            connector, record, bios = extract.load_records(project)
        except NasError:
            pass  # offline / API hiccup: extraction continues without biospecimens
    entry = _entry(cfg, prov.get("dataset_id"))
    st, samples, gaps = extract.build_draft(cfg, project, entry, connector, record, prov.get("meta"), bios,
                                            prov.get("policy"), prov.get("policy_ack"))
    errors = schema.validate(st)
    (meta / "study.draft.json").write_text(json.dumps(st, indent=1))
    n = schema.write_samples(meta / "samples.draft.tsv", samples) if samples else 0
    if not (meta / "study.json").exists():
        index.upsert(cfg, st)  # drafts are searchable until a curated record replaces them
    return {"project": str(project), "draft": "metadata/study.draft.json", "gaps": gaps,
            "samples_rows": n, "samples_draft": "metadata/samples.draft.tsv" if n else None,
            "schema_errors": errors, "study": st}


def inspect_files(cfg: Config, project_ref: str, max_files: int = 30, include_raw_counts: bool = True) -> dict:
    project = resolve_project(cfg, project_ref)
    out = {"project": str(project), "files": insp.inspect_project(project, max_files)}
    if include_raw_counts:
        out["inventory"] = insp.inventory(project)
    return out


def lookup_terms(terms: list[dict], http: Http | None = None, rows: int = 3) -> list[dict]:
    http = http or Http()
    res = []
    for t in terms[:40]:
        field, text = t.get("field"), t.get("text")
        if not field or not text:
            raise NasError("Each term needs {field, text}; field is one of " + ", ".join(ontology.FIELD_ONTOLOGIES))
        res.append(ontology.lookup(http, field, text, rows))
    return res


def save(cfg: Config, project_ref: str, study: dict, samples: list[dict] | None = None,
         use_draft_samples: bool = True, status: str = "curated", curated_by: str = "Claude (study-metadata-curation)") -> dict:
    project = resolve_project(cfg, project_ref)
    meta = _meta_dir(project)
    st = json.loads(json.dumps(study))  # deep copy
    idn = st.setdefault("identity", {})
    if (idn.get("source"), idn.get("project_code")) != (project.parent.name, project.name):
        raise NasError(f"identity.source/project_code must be {project.parent.name!r}/{project.name!r}.")
    st["schema_version"] = schema.SCHEMA_VERSION
    cur = st.setdefault("curation", {})
    cur.update({"status": status, "curated_by": curated_by, "curated_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
    st.setdefault("data", {}).update({"levels": insp.inventory(project), "nas_path": str(project)})
    rows = samples
    if rows is None and use_draft_samples:
        rows = schema.read_samples(meta / "samples.draft.tsv") or schema.read_samples(meta / "samples.tsv") or None
    st["data"]["has_samples_table"] = bool(rows)
    if cfg.client_root:
        from ..paths import to_client
        st["data"]["client_path"] = to_client(cfg, project)
    errors = schema.validate(st)
    if errors:
        return {"saved": False, "schema_errors": errors,
                "hint": "Fix these fields and call nas_save_metadata again; nothing was written."}
    if rows:
        for i, r in enumerate(rows):
            if not str(r.get("sample_id") or "").strip():
                return {"saved": False, "schema_errors": [f"samples[{i}]: sample_id is required"]}
    (meta / "study.json").write_text(json.dumps(st, indent=1))
    n = schema.write_samples(meta / "samples.tsv", rows) if rows else 0
    index.upsert(cfg, st)
    return {"saved": True, "study": "metadata/study.json", "samples_rows": n,
            "remaining_gaps": extract.gaps(st), "catalog": str(cfg.omics_root / "CATALOG.tsv")}
