"""Deterministic first-pass metadata from saved source records + files on disk.

Produces a draft ADMS study record, a samples table when the source provides one (PDC biospecimens,
SDRF files, CELLxGENE donors), and the list of standard fields still empty ("gaps") for Claude to
fill with evidence during curation.
"""
from __future__ import annotations

import html
import json
import re
import time
from pathlib import Path

from ..config import Config
from ..paths import to_client
from .inspect import inventory, read_sdrf_samples
from .ontology import newt_to_ncbitaxon
from .schema import SCHEMA_VERSION


NO_ID = {"unknown", "na", "n/a", "not applicable", "not reported", ""}


def _t(label, cid=None, ontology=None, verbatim=None) -> dict:
    d = {"label": str(label).strip()}
    if cid and str(cid).strip().lower() not in NO_ID:  # CELLxGENE uses 'unknown'/'na' as placeholder ids
        d["id"] = cid
        d["ontology"] = ontology or cid.split(":")[0]
    if verbatim and verbatim != d["label"]:
        d["verbatim"] = verbatim
    return d


def _cv_terms(items) -> list[dict]:
    out = []
    for it in items or []:
        acc, name = it.get("accession", ""), it.get("name", "")
        if not name:
            continue
        tax = newt_to_ncbitaxon(acc) if acc.startswith("NEWT") else None
        cid = tax or (acc if re.match(r"^[A-Za-z]+:\S+$", acc) else None)
        label = re.sub(r"\s*\(.*?\)\s*$", "", name) if tax else name
        out.append(_t(label, cid, verbatim=name))
    return out


def _uniq(terms: list[dict]) -> list[dict]:
    seen, out = set(), []
    for t in terms:
        k = (t.get("id") or t["label"]).lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out


def _clean(text) -> str | None:
    if not text:
        return None
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(text)))).strip() or None


def _ev(evidence: dict, fields: list[str], detail: str, source="api", confidence="high") -> None:
    for f in fields:
        evidence[f] = {"source": source, "detail": detail, "confidence": confidence}


# ------------------------------------------------------------------ per-source mappers
def from_pride(rec: dict, st: dict, ev: dict) -> None:
    idn, bio, assay = st["identity"], st["biology"], st["assay"]
    idn["title"] = _clean(rec.get("title")) or idn["title"]
    idn["description"] = _clean(rec.get("projectDescription"))
    idn["keywords"] = [k for k in rec.get("keywords", []) if k][:30]
    idn["license"] = rec.get("license") if isinstance(rec.get("license"), str) else idn.get("license")
    pubs = []
    for r in rec.get("references") or []:
        pm = str(r.get("pubmedID") or "")
        pubs.append({"pmid": pm if pm not in ("", "0") else None, "doi": r.get("doi") or None,
                     "citation": r.get("referenceLine")})
    idn["publications"] = pubs
    idn["contacts"] = [{"name": f"{p.get('firstName', '')} {p.get('lastName', '')}".strip(),
                        "affiliation": p.get("affiliation"), "role": "lab PI"} for p in rec.get("labPIs") or []]
    bio["organism"] = _uniq(_cv_terms(rec.get("organisms")))
    bio["tissue"] = _uniq(_cv_terms(rec.get("organismParts")))
    bio["disease"] = _uniq(_cv_terms(rec.get("diseases")))
    assay["technology"] = _uniq(_cv_terms(rec.get("instruments")))
    assay["software"] = _uniq(_cv_terms(rec.get("softwares")))
    types = [t.get("name", "") for t in rec.get("experimentTypes") or []]
    # word-boundary patterns: "data-independent" must not also match "dependent acquisition" (DDA)
    acq_pats = (("DIA", r"\bdata[- ]independent|\bDIA\b"), ("DDA", r"\bdata[- ]dependent|\bDDA\b"),
                ("PRM", r"parallel reaction|\bPRM\b"), ("SRM", r"selected reaction|\b[SM]RM\b"), ("TMT", r"\bTMT"))
    acq = [a for a, pat in acq_pats if any(re.search(pat, t, re.I) for t in types)]
    assay["acquisition"] = acq
    assay["quantification"] = [q.get("name") for q in rec.get("quantificationMethods") or [] if q.get("name")]
    prot = " ".join(filter(None, [rec.get("sampleProcessingProtocol"), rec.get("dataProcessingProtocol")]))
    assay["protocol_summary"] = _clean(prot)[:2000] if prot else None
    if any("phospho" in (t or "").lower() for t in types + idn["keywords"]):
        assay["modality"].append("phosphoproteomics")
    ev_fields = ["identity.title", "identity.description", "identity.publications", "biology.organism",
                 "assay.technology", "assay.software", "assay.acquisition"]
    ev_fields += [f for f, v in (("biology.tissue", bio["tissue"]), ("biology.disease", bio["disease"])) if v]
    _ev(ev, ev_fields, "PRIDE Archive v3 project record")
    st["extensions"]["pride"] = {"submissionType": rec.get("submissionType"), "experimentTypes": types,
                                 "modifications": [m.get("name") for m in rec.get("identifiedPTMStrings") or []
                                                   if isinstance(m, dict)][:30]}


def from_pdc(rec: dict, st: dict, ev: dict, biospecimens: list[dict] | None) -> list[dict]:
    s = rec.get("study", {})
    idn, bio, assay, des = st["identity"], st["biology"], st["assay"], st["design"]
    idn["title"] = s.get("study_name") or idn["title"]
    idn["consortium"] = s.get("program_name")
    idn["accessions"] = [a for a in (s.get("pdc_study_id"), s.get("study_id")) if a]
    bio["organism"] = [_t("Homo sapiens", "NCBITaxon:9606")]
    bio["disease"] = [_t(d) for d in (s.get("disease_type") or "").split(";") if d and d not in ("Other", "Not Reported")]
    bio["tissue"] = [_t(t) for t in (s.get("primary_site") or "").split(";") if t and t != "Not Reported"]
    assay["fractions"] = [s["analytical_fraction"]] if s.get("analytical_fraction") else []
    if s.get("analytical_fraction", "").lower().startswith("phospho"):
        assay["modality"].append("phosphoproteomics")
    assay["quantification"] = [s["experiment_type"]] if s.get("experiment_type") else []
    des["n_subjects"] = s.get("cases_count")
    des["n_samples"] = s.get("aliquots_count")
    _ev(ev, ["identity.title", "biology.disease", "biology.tissue", "assay.quantification", "design.n_subjects",
             "design.n_samples"], "PDC GraphQL study record")
    samples = []
    for b in biospecimens or []:
        samples.append({"sample_id": b.get("aliquot_submitter_id"), "subject_id": b.get("case_submitter_id"),
                        "organism": b.get("taxon"), "tissue": b.get("primary_site"),
                        "sample_type": b.get("sample_type"), "disease": b.get("disease_type"),
                        "char:sample_submitter_id": b.get("sample_submitter_id"), "char:pool": b.get("pool"),
                        "comment:aliquot_id": b.get("aliquot_id")})
    if samples:
        types = sorted({r["sample_type"] for r in samples if r.get("sample_type")})
        bio["sample_type"] = [_t(x) for x in types if x != "Not Reported"]
        _ev(ev, ["biology.sample_type"], "PDC biospecimenPerStudy")
    return samples


def from_cellxgene(rec: dict, st: dict, ev: dict) -> list[dict]:
    idn, bio, assay, des = st["identity"], st["biology"], st["assay"], st["design"]
    ds = rec.get("datasets") or []
    if rec.get("name"):
        idn["title"] = rec["name"]
    idn["description"] = _clean(rec.get("description"))
    idn["doi"] = rec.get("doi")
    idn["consortium"] = ", ".join(rec.get("consortia") or []) or None
    idn["urls"] = [u for u in [rec.get("collection_url")] if u]
    authors = (rec.get("publisher_metadata") or {}).get("authors") or []
    if authors:
        idn["publications"] = [{"doi": rec.get("doi"), "citation": f"{authors[0].get('family')} et al.",
                                "pmid": None, "title": None}]

    def agg(key, cap=60):
        out = []
        for d in ds:
            for x in d.get(key) or []:
                if isinstance(x, dict) and x.get("label"):
                    out.append(_t(x["label"], x.get("ontology_term_id")))
        return _uniq(out)[:cap]

    for field, key in (("organism", "organism"), ("tissue", "tissue"), ("disease", "disease"), ("cell_type", "cell_type"),
                       ("sex", "sex"), ("development_stage", "development_stage"), ("ancestry", "self_reported_ethnicity")):
        bio[field] = agg(key)
    assay["technology"] = agg("assay")
    labels = " ".join(t["label"].lower() for t in assay["technology"])
    susp = {s for d in ds for s in (d.get("suspension_type") or [])}
    mod = []
    if any(k in labels for k in ("visium", "slide-seq", "merfish", "xenium", "stereo")):
        mod.append("spatial_transcriptomics")
    if "multiome" in labels:
        mod.append("multiome")
    if "nucleus" in susp:
        mod.append("snRNA-seq")
    if "cell" in susp or not mod:
        mod.append("scRNA-seq")
    assay["modality"] = list(dict.fromkeys(mod))
    assay["feature_type"] = "gene"
    des["n_cells"] = sum(int(d.get("cell_count") or 0) for d in ds) or None
    donors = {x for d in ds for x in (d.get("donor_id") or [])}
    des["n_subjects"] = len(donors) or None
    st["extensions"]["cellxgene"] = {"schema_versions": sorted({d.get("schema_version") for d in ds if d.get("schema_version")}),
                                     "n_datasets": len(ds)}
    _ev(ev, ["identity.title", "identity.doi", "biology.organism", "biology.tissue", "biology.disease",
             "biology.cell_type", "biology.sex", "assay.technology", "assay.modality", "design.n_cells",
             "design.n_subjects"], "CELLxGENE curation API (ontology ids from the CELLxGENE schema)")
    samples = []
    for d in ds:
        samples.append({"sample_id": d.get("dataset_id"), "tissue": "; ".join(x["label"] for x in d.get("tissue") or []),
                        "disease": "; ".join(x["label"] for x in d.get("disease") or []),
                        "organism": "; ".join(x["label"] for x in d.get("organism") or []),
                        "cell_type": "; ".join(x["label"] for x in (d.get("cell_type") or [])[:5]),
                        "char:title": d.get("title"), "char:cell_count": d.get("cell_count"),
                        "char:assay": "; ".join(x["label"] for x in d.get("assay") or []),
                        "char:n_donors": len(d.get("donor_id") or [])})
    return samples  # one row per CELLxGENE dataset (h5ad); donor-level rows come from the h5ad obs


def from_zenodo(rec: dict, st: dict, ev: dict) -> None:
    md, idn = rec.get("metadata", {}), st["identity"]
    idn["title"] = md.get("title") or idn["title"]
    idn["description"] = _clean(md.get("description"))
    idn["doi"] = rec.get("doi")
    idn["version"] = md.get("version")
    lic = md.get("license")
    idn["license"] = lic.get("id") if isinstance(lic, dict) else lic
    idn["keywords"] = md.get("keywords") or []
    idn["contacts"] = [{"name": c.get("name", ""), "affiliation": c.get("affiliation"), "role": "creator"}
                       for c in md.get("creators") or []][:20]
    _ev(ev, ["identity.title", "identity.description", "identity.doi", "identity.license"], "Zenodo record")


def from_hf(rec: dict, st: dict, ev: dict) -> None:
    card, idn = rec.get("cardData") or {}, st["identity"]
    idn["title"] = rec.get("id") or idn["title"]
    idn["license"] = card.get("license")
    idn["version"] = rec.get("sha")
    idn["keywords"] = [t for t in rec.get("tags", []) if ":" not in t][:30]
    _ev(ev, ["identity.title", "identity.license", "identity.version"], "Hugging Face dataset card")


def from_proxi(rec: dict, st: dict, ev: dict) -> None:
    idn, bio, assay = st["identity"], st["biology"], st["assay"]
    idn["title"] = rec.get("title") or idn["title"]
    idn["description"] = _clean(rec.get("summary"))
    idn["keywords"] = [k.get("value") for k in rec.get("keywords") or [] if k.get("value")][:30]
    for sp in rec.get("species") or []:
        vals = {x.get("name"): x.get("value") for x in sp}
        tax = vals.get("taxonomy: NCBI TaxID")
        name = vals.get("taxonomy: scientific name")
        if name:
            bio.setdefault("organism", []).append(_t(name, f"NCBITaxon:{tax}" if tax else None))
    assay["technology"] = _uniq(_cv_terms(rec.get("instruments")))
    pubs = []
    for pub in rec.get("publications") or []:
        vals = {x.get("name"): x.get("value") for x in pub}
        pubs.append({"pmid": vals.get("PubMed identifier"), "citation": vals.get("Reference"), "doi": None})
    idn["publications"] = pubs
    _ev(ev, ["identity.title", "identity.description", "biology.organism", "assay.technology"], "MassIVE PROXI record")


DEFAULT_MODALITY = {"pride": "ms_proteomics", "massive": "ms_proteomics", "pdc": "ms_proteomics",
                    "cellxgene": "scRNA-seq", "zenodo": "other", "huggingface": "other", "s3": "other",
                    "urls": "other", "synapse": "other"}
ENTRY_MODALITY = [("olink", "affinity_proteomics"), ("somascan", "affinity_proteomics"), ("pqtl", "gwas_summary_statistics"),
                  ("cell painting", "imaging_phenotypic"), ("snrna", "snRNA-seq"), ("scrna", "scRNA-seq"),
                  ("single cell", "scRNA-seq"), ("single-cell", "scRNA-seq"), ("merfish", "spatial_transcriptomics"),
                  ("perturb", "scRNA-seq"), ("tmt", "ms_proteomics"), ("mass spectrometry", "ms_proteomics"),
                  ("proteomics", "ms_proteomics"), ("crispr", "genomics")]


def _modality_from_entry(entry: dict, connector: str) -> list[str]:
    text = f"{entry.get('modality', '')} {entry.get('keywords', '')}".lower()
    hits = [m for k, m in ENTRY_MODALITY if k in text]
    return list(dict.fromkeys(hits))[:3] or [DEFAULT_MODALITY.get(connector, "other")]


# ------------------------------------------------------------------ orchestration
def gaps(st: dict) -> list[str]:
    mods = set(st["assay"].get("modality") or [])
    want = ["identity.description", "identity.license", "identity.publications", "biology.organism",
            "biology.disease", "biology.sample_type", "assay.technology", "design.n_samples", "design.study_type"]
    if mods & {"scRNA-seq", "snRNA-seq", "multiome", "spatial_transcriptomics"}:
        want = [w for w in want if w != "biology.sample_type"] + ["biology.tissue", "biology.cell_type", "design.n_cells"]
    if mods & {"ms_proteomics", "phosphoproteomics", "single_cell_proteomics"}:
        want += ["assay.acquisition", "assay.quantification"]
    if mods & {"affinity_proteomics"}:
        want += ["assay.quantification"]
    out = []
    for path in want:
        sec, key = path.split(".")
        if st.get(sec, {}).get(key) in (None, [], "", {}):
            out.append(path)
    return out


def build_draft(cfg: Config, project: Path, entry: dict | None, connector: str | None, record: dict | None,
                plan_meta: dict | None = None, biospecimens: list[dict] | None = None,
                policy: str | None = None, dua_reference: str | None = None) -> tuple[dict, list[dict], list[str]]:
    source, code = project.parent.name, project.name
    entry = entry or {}
    plan_meta = plan_meta or {}
    st: dict = {
        "schema_version": SCHEMA_VERSION,
        "identity": {"source": source, "project_code": code, "registry_id": entry.get("id"),
                     "accessions": [code], "title": plan_meta.get("title") or entry.get("name") or f"{source} {code}",
                     "license": plan_meta.get("license"), "access_policy": policy or entry.get("local_download"),
                     "dua_reference": dua_reference, "urls": [u for u in (plan_meta.get("source_url"), entry.get("docs")) if u]},
        "biology": {}, "assay": {"modality": _modality_from_entry(entry, connector or "")}, "design": {},
        "data": {}, "curation": {"status": "draft", "curated_by": "nas-mcp extract (deterministic)",
                                 "curated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "field_evidence": {},
                                 "needs_review": []},
        "extensions": {},
    }
    ev = st["curation"]["field_evidence"]
    samples: list[dict] = []
    rec = record or {}
    if connector == "pride" and rec:
        from_pride(rec, st, ev)
    elif connector == "pdc" and rec:
        samples = from_pdc(rec, st, ev, biospecimens)
    elif connector == "cellxgene" and rec:
        samples = from_cellxgene(rec, st, ev)
    elif connector == "zenodo" and rec:
        from_zenodo(rec, st, ev)
    elif connector == "huggingface" and rec:
        from_hf(rec, st, ev)
    elif connector == "massive" and rec:
        from_proxi(rec, st, ev)
    st["assay"]["modality"] = list(dict.fromkeys(st["assay"]["modality"]))

    # SDRF files on disk beat everything for sample-level metadata (proteomics standard)
    sdrfs = sorted((project / "metadata").rglob("*sdrf*.tsv")) if (project / "metadata").is_dir() else []
    if sdrfs:
        samples = read_sdrf_samples(sdrfs[0])
        st["curation"]["field_evidence"]["samples"] = {"source": "file", "detail": str(sdrfs[0].relative_to(project)),
                                                        "confidence": "high"}
        des = st["design"]
        des["n_samples"] = des.get("n_samples") or len({r.get("sample_id") for r in samples if r.get("sample_id")})
        for fld, col in (("disease", "disease"), ("tissue", "tissue"), ("cell_type", "cell_type")):
            vals = sorted({r.get(col) for r in samples if r.get(col) and r.get(col).lower() not in ("not available", "not applicable")})
            if vals and not st["biology"].get(fld):
                st["biology"][fld] = [_t(v) for v in vals[:40]]
                ev[f"biology.{fld}"] = {"source": "file", "detail": "SDRF characteristics (labels not yet normalised)",
                                        "confidence": "medium"}

    inv = inventory(project)
    st["data"] = {"levels": inv, "nas_path": str(project), "client_path": to_client(cfg, project) if cfg.client_root else None,
                  "has_samples_table": bool(samples)}
    missing = gaps(st)
    st["curation"]["needs_review"] = missing
    return st, samples, missing


def load_records(project: Path) -> tuple[str | None, dict | None, list[dict] | None]:
    src = project / "metadata" / "source"
    if not src.is_dir():
        return None, None, None
    rec_files = sorted(p for p in src.glob("*.json") if not p.name.startswith(("biospecimens", "_")))
    if not rec_files:
        return None, None, None
    connector = rec_files[0].stem
    bios = src / "biospecimens.json"
    return connector, json.loads(rec_files[0].read_text()), (json.loads(bios.read_text()) if bios.exists() else None)
