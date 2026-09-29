"""Database layout:  <database root>/<SOURCE>/<PROJECT_CODE>/{raw,processed,metadata}/...

  raw/        instrument or sequencer output, spectra, images (.raw .d .wiff .mzML .mgf .fastq .bam .tif ...)
  processed/  results and derived tables/matrices (.tsv .csv .parquet .h5ad .rds .mzTab .mzid search outputs ...)
  metadata/   study/sample descriptions: SDRF, README, source API records, study.json, samples.tsv
Top level of each project: PROVENANCE.md and files.tsv.  Database-wide: _catalog/ (index + CATALOG.tsv).
"""
from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from . import NasError
from .config import Config
from .manifest import FileEntry
from .paths import component

LEVELS = ("raw", "processed", "metadata")
RESERVED = {"_catalog"}

RAW_EXT = {".raw", ".d", ".wiff", ".wiff2", ".scan", ".mzml", ".mzxml", ".mgf", ".ms2", ".dia", ".baf", ".tdf",
           ".tdf_bin", ".fastq", ".fq", ".bam", ".cram", ".sra", ".fast5", ".pod5", ".bcl", ".cbcl",
           ".tif", ".tiff", ".nd2", ".czi", ".ome.tif", ".ome.tiff", ".adat"}
META_NAMES = re.compile(r"(sdrf|readme|manifest|metadata|sample[_-]?info|samples?\.(tsv|csv|txt)|design|"
                        r"clinical|phenotype|annotation|changelog|license|citation|checksums?|md5)", re.I)
META_EXT = {".md", ".html", ".pdf", ".docx", ".json", ".yaml", ".yml", ".xml"}

PRIDE_LEVEL = {"RAW": "raw", "PEAK": "raw", "EXPERIMENTAL DESIGN": "metadata", "SEARCH": "processed",
               "RESULT": "processed", "QUANT": "processed", "FASTA": "processed", "SPECTRUM_LIBRARY": "processed",
               "OTHER": None}
PDC_LEVEL = {"Raw Mass Spectra": "raw", "Processed Mass Spectra": "raw", "Other Metadata": "metadata",
             "Publication Supplementary Material": "metadata"}


def _ext(name: str) -> str:
    n = name.lower()
    for comp in (".gz", ".bz2", ".xz", ".zst", ".zip"):
        if n.endswith(comp) and n[: -len(comp)].rsplit("/", 1)[-1].count("."):
            n = n[: -len(comp)]
            break
    for double in (".ome.tif", ".ome.tiff"):
        if n.endswith(double):
            return double
    return PurePosixPath(n).suffix


def classify(f: FileEntry, connector: str = "") -> str:
    name = PurePosixPath(f.relpath).name
    cat = (f.attrs or {}).get("category")
    if connector == "pride" and cat in PRIDE_LEVEL and PRIDE_LEVEL[cat]:
        return PRIDE_LEVEL[cat]
    if connector == "pdc" and cat:
        return PDC_LEVEL.get(cat, "processed")
    if META_NAMES.search(name):
        return "metadata"
    ext = _ext(name)
    if ext in RAW_EXT or any(p.lower().endswith(".d") for p in PurePosixPath(f.relpath).parts[:-1]):
        return "raw"
    if ext in META_EXT:
        return "metadata"
    return "processed"


def _derived(params: dict) -> dict:
    d = dict(params)
    parts = [p for p in str(params.get("prefix") or "").split("/") if p]
    for i, p in enumerate(parts, 1):
        d[f"prefix_{i}"] = p
    if params.get("repo"):
        d["repo_name"] = str(params["repo"]).split("/")[-1]
    return d


class _Strict(dict):
    def __missing__(self, key):
        raise KeyError(key)


def project_location(cfg: Config, entry: dict, params: dict, project_code: str | None = None,
                     source: str | None = None) -> tuple[str, str, Path]:
    """Return (SOURCE, PROJECT_CODE, absolute project dir) for a registry entry + params."""
    if source and not entry.get("source_override"):
        raise NasError(f"The source folder for {entry['id']} is fixed to {entry.get('source_folder')!r}.")
    src = component(source or entry.get("source_folder") or entry["id"], "source folder")
    if project_code:
        code = component(project_code, "project code")
    else:
        tmpl = entry.get("project_code") or "{project_code}"
        try:
            code = component(tmpl.format_map(_Strict(_derived(params))), "project code")
        except KeyError as e:
            raise NasError(
                f"{entry['id']} needs a project code for its folder (template {tmpl!r}, missing {e}). "
                "Pass project_code, e.g. a release/version or a short study code."
            ) from None
    if src in RESERVED:
        raise NasError(f"{src} is reserved.")
    return src, code, cfg.omics_root / src / code


def resolve_project(cfg: Config, project: str) -> Path:
    """Accept 'SOURCE/PROJECT', a NAS path or a client (Mac) path; return the project dir."""
    from .paths import resolve_dest, to_nas
    raw = to_nas(cfg, project.strip().rstrip("/"))
    p = Path(raw) if raw.startswith("/") else cfg.omics_root / raw
    p = resolve_dest(cfg, str(p))
    try:
        rel = p.relative_to(cfg.omics_root.resolve())
    except ValueError:
        raise NasError(f"{project} is not inside the database root {cfg.omics_root}.") from None
    if len(rel.parts) != 2 or rel.parts[0] in RESERVED:
        raise NasError(f"Expected <SOURCE>/<PROJECT_CODE> under the database root, got {rel}.")
    if not p.is_dir():
        raise NasError(f"Project folder {p} does not exist.")
    return p
