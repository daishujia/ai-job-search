"""NCI Proteomic Data Commons (CPTAC) via GraphQL.

Observed behaviour (2026-09): filesPerStudy needs the study UUID (study_id); requesting
signedUrl for a whole study can fail server-side, so URLs are fetched per data_category.
Signed URLs are valid for several days; re-plan to refresh them if a job stalls on 403s.
"""
from __future__ import annotations

from collections import defaultdict

from .. import NasError
from ..manifest import FileEntry, human
from .base import Listing, require

GQL = "https://pdc.cancer.gov/graphql"


def _q(http, query: str) -> dict:
    d = http.post_json(GQL, {"query": query})
    if d.get("errors") and not d.get("data"):
        raise NasError(f"PDC GraphQL error: {d['errors'][0].get('message')}")
    return d


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def list_files(params: dict, http, cfg) -> Listing:
    pdc_id = require(params, "pdc_study_id", r"PDC\d{6}", "PDC000127")
    wanted = [c for c in params.get("data_categories") or []]
    st = _q(http, f'{{ study(pdc_study_id: "{pdc_id}", acceptDUA: true) '
                  '{ study_id pdc_study_id study_name program_name project_name disease_type primary_site '
                  'analytical_fraction experiment_type cases_count aliquots_count } }')["data"]["study"]
    if not st:
        raise NasError(f"PDC study {pdc_id} not found.")
    study = st[0]
    sid = study["study_id"]
    listing = _q(http, f'{{ filesPerStudy(study_id: "{sid}", acceptDUA: true) '
                       '{ file_id file_name file_size md5sum data_category file_type file_format } }')
    all_files = listing["data"]["filesPerStudy"] or []
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for f in all_files:
        by_cat[f.get("data_category") or "Unknown"].append(f)
    if not wanted:
        cats = {c: {"files": len(v), "size": human(sum(int(x.get("file_size") or 0) for x in v))}
                for c, v in sorted(by_cat.items())}
        raise NasError(
            f"PDC study {pdc_id} ({study['study_name']}) has these data_categories: {cats}. "
            "Re-run with params.data_categories, e.g. ['Protein Assembly'] for processed tables "
            "(small) or ['Raw Mass Spectra'] (large)."
        )
    unknown = [c for c in wanted if c not in by_cat]
    if unknown:
        raise NasError(f"Unknown data_categories {unknown}; available: {sorted(by_cat)}")
    meta_by_id = {f["file_id"]: f for f in all_files}
    files: list[FileEntry] = []
    missing = 0
    for cat in wanted:
        d = _q(http, f'{{ filesPerStudy(study_id: "{sid}", data_category: "{_esc(cat)}", acceptDUA: true) '
                     '{ file_id file_name signedUrl { url } } }')
        for f in d["data"]["filesPerStudy"] or []:
            url = ((f.get("signedUrl") or {}).get("url"))
            if not url:
                missing += 1
                continue
            m = meta_by_id.get(f["file_id"], f)
            md5 = (m.get("md5sum") or "").lower() or None
            files.append(FileEntry(
                url=url, relpath=f"{cat}/{f['file_name']}",
                size=int(m["file_size"]) if m.get("file_size") else None,
                checksum_type="md5" if md5 else None, checksum=md5,
                attrs={"file_id": f["file_id"], "category": cat},
            ))
    return Listing(files=files, record={"study": study}, meta={
        "title": study["study_name"], "accession": pdc_id,
        "disease": study.get("disease_type"), "site": study.get("primary_site"),
        "source_url": f"https://pdc.cancer.gov/pdc/study/{pdc_id}",
        "license": "PDC data use: cite CPTAC/PDC per https://pdc.cancer.gov/pdc/faq",
        "notes": f"{missing} file(s) had no signed URL and were skipped." if missing else "",
    })
