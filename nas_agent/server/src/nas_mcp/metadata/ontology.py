"""Ontology normalisation via EBI OLS4 (public, no key) + fixed mappings for common source CVs."""
from __future__ import annotations

import re

OLS = "https://www.ebi.ac.uk/ols4/api/search"

# Which ontologies to search for each standard field (first = preferred, as in CELLxGENE / SDRF).
FIELD_ONTOLOGIES = {
    "organism": ["ncbitaxon"],
    "tissue": ["uberon"],
    "sample_type": ["uberon", "efo", "obi"],
    "cell_type": ["cl"],
    "cell_line": ["clo", "efo"],
    "disease": ["mondo", "efo"],
    "sex": ["pato"],
    "development_stage": ["hsapdv", "mmusdv", "efo"],
    "ancestry": ["hancestro"],
    "technology": ["efo", "ms", "obi"],
    "software": ["ms", "swo"],
    "perturbation": ["chebi", "efo"],
}

FIXED = {  # very common values; avoids a network call and keeps ids consistent
    ("disease", "normal"): ("normal", "PATO:0000461"), ("disease", "healthy"): ("normal", "PATO:0000461"),
    ("disease", "control"): ("normal", "PATO:0000461"),
    ("sex", "female"): ("female", "PATO:0000383"), ("sex", "male"): ("male", "PATO:0000384"),
    ("organism", "homo sapiens"): ("Homo sapiens", "NCBITaxon:9606"), ("organism", "human"): ("Homo sapiens", "NCBITaxon:9606"),
    ("organism", "mus musculus"): ("Mus musculus", "NCBITaxon:10090"), ("organism", "mouse"): ("Mus musculus", "NCBITaxon:10090"),
    ("sample_type", "plasma"): ("blood plasma", "UBERON:0001969"), ("sample_type", "blood plasma"): ("blood plasma", "UBERON:0001969"),
    ("sample_type", "serum"): ("blood serum", "UBERON:0001977"),
    ("sample_type", "csf"): ("cerebrospinal fluid", "UBERON:0001359"),
    ("sample_type", "cerebrospinal fluid"): ("cerebrospinal fluid", "UBERON:0001359"),
}


def newt_to_ncbitaxon(accession: str) -> str | None:
    m = re.fullmatch(r"(?:NEWT|NCBITaxon|taxonomy):?(\d+)", accession or "")
    return f"NCBITaxon:{m.group(1)}" if m else None


def lookup(http, field: str, text: str, rows: int = 3) -> dict:
    text = (text or "").strip()
    key = (field, text.lower())
    if key in FIXED:
        label, cid = FIXED[key]
        return {"field": field, "text": text, "candidates": [{"label": label, "id": cid, "ontology": cid.split(":")[0].lower(),
                                                              "exact": True}]}
    onts = FIELD_ONTOLOGIES.get(field)
    if not onts:
        return {"field": field, "text": text, "candidates": [], "note": f"no ontology configured for '{field}'"}
    d = http.get_json(OLS, params={"q": text, "ontology": ",".join(onts), "rows": str(rows * 2),
                                   "fieldList": "label,obo_id,ontology_name,description,synonym",
                                   "queryFields": "label,synonym"})
    cands = []
    for doc in d.get("response", {}).get("docs", []):
        if not doc.get("obo_id"):
            continue
        label = doc.get("label", "")
        syns = [s.lower() for s in doc.get("synonym") or []]
        cands.append({"label": label, "id": doc["obo_id"], "ontology": doc.get("ontology_name"),
                      "exact": label.lower() == text.lower() or text.lower() in syns,
                      "definition": (doc.get("description") or [""])[0][:200]})
    cands.sort(key=lambda c: (not c["exact"], onts.index(c["ontology"]) if c["ontology"] in onts else 99))
    return {"field": field, "text": text, "candidates": cands[:rows]}
