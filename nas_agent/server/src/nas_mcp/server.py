"""nas-mcp: MCP server (stdio) for NAS storage + large omics dataset downloads via aria2.

Run on the NAS; connect from Claude Code over SSH:
  claude mcp add nas -- ssh agent@192.168.86.28 ~/nas-mcp/.venv/bin/nas-mcp
"""
from __future__ import annotations

import functools
import json
import logging
import os
from typing import Annotated, Any, Callable, Literal

import anyio
from pydantic import Field

try:  # MCP Python SDK v2
    from mcp.server.mcpserver import MCPServer as _Server
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:  # v1.x maintenance line
    from mcp.server.fastmcp import FastMCP as _Server
    from mcp.server.fastmcp.exceptions import ToolError

from . import NasError, ingest, jobs, planning, registry, storage, verify
from .metadata import index as mindex
from .metadata import service as msvc
from .paths import to_client
from .config import Config, load_config
from .manifest import Plan

logging.getLogger("httpx").setLevel(logging.WARNING)  # keep stderr quiet over SSH
mcp = _Server("nas_mcp")
_cfg: Config | None = None

RO = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
RO_NET = {**RO, "openWorldHint": True}
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True}


def cfg() -> Config:
    global _cfg
    if _cfg is None:
        _cfg = load_config()
    return _cfg


async def _run(fn: Callable[..., Any], *a: Any, **kw: Any) -> str:
    """Run blocking work off the event loop; turn NasError into a readable tool error."""
    try:
        out = await anyio.to_thread.run_sync(functools.partial(fn, *a, **kw))
    except NasError as e:  # deliberate, actionable: the message reaches the model
        raise ToolError(str(e)) from None
    return json.dumps(out, indent=1, default=str)


# ------------------------------------------------------------------ storage
@mcp.tool(name="nas_storage_overview", annotations=RO)
async def nas_storage_overview() -> str:
    """Capacity, used and free space for each NAS volume / allowed root (warns above 80% used), plus the
    database root as the NAS and the Mac see it."""
    return await _run(storage.overview, cfg())


@mcp.tool(name="nas_list_folders", annotations=RO)
async def nas_list_folders(
    path: Annotated[str | None, Field(description="Folder to list; relative paths are under the omics root. Default: omics root.")] = None,
    depth: Annotated[int, Field(ge=1, le=4, description="How many levels deep to list.")] = 1,
) -> str:
    """List sub-folders inside the allowed roots so the user can pick a download destination."""
    return await _run(storage.list_folders, cfg(), path, depth)


@mcp.tool(name="nas_folder_usage", annotations=RO)
async def nas_folder_usage(path: Annotated[str, Field(description="Folder inside the allowed roots.")]) -> str:
    """Total size, file count and largest sub-folders of a folder (stops after ~20 s on huge trees)."""
    return await _run(storage.folder_usage, cfg(), path)


@mcp.tool(name="nas_create_folder",
          annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
async def nas_create_folder(path: Annotated[str, Field(description="Folder to create (inside allowed roots).")]) -> str:
    """Create a destination folder (with parents). Never overwrites anything."""
    return await _run(storage.create_folder, cfg(), path)


# ------------------------------------------------------------------ catalog / planning
@mcp.tool(name="nas_catalog_search", annotations=RO)
async def nas_catalog_search(
    query: Annotated[str, Field(description="Words to match, e.g. 'alzheimer single cell', 'olink', 'cptac'. Empty = all.")] = "",
) -> str:
    """Search the dataset registry: ids, access policy (allowed/summary_only/check_dua/forbidden), connector, defaults."""
    return await _run(registry.search, cfg(), query)


@mcp.tool(name="nas_browse_source", annotations=RO_NET)
async def nas_browse_source(
    dataset_id: Annotated[str, Field(description="Registry id, e.g. 'sea-ad', 'jump-cellpainting', 'cptac-pdc'.")],
    params: Annotated[dict | None, Field(description="Connector params, e.g. {'prefix': 'MTG/'} or {'pdc_study_id': 'PDC000127'}.")] = None,
) -> str:
    """Peek inside a source before planning: S3 sub-folders, or PDC data categories with sizes."""
    return await _run(planning.browse, cfg(), dataset_id, params)


LEVELS_FIELD = Field(description="Keep only these data levels: 'raw' (instrument/sequencer output), 'processed' "
                               "(results, matrices, h5ad), 'metadata' (always included). Default: all.")


@mcp.tool(name="nas_plan_dataset", annotations=RO_NET)
async def nas_plan_dataset(
    dataset_id: Annotated[str, Field(description="Registry id from nas_catalog_search (e.g. 'pride', 'cptac-pdc', 'sea-ad', 'tahoe-100m', 'cellxgene-discover').")],
    params: Annotated[dict | None, Field(description=(
        "Connector params. pride: {accession:'PXD046444', categories:['RAW','RESULT']}; "
        "pdc: {pdc_study_id:'PDC000127', data_categories:['Protein Assembly']}; "
        "s3: {prefix:'MTG/RNAseq/'}; huggingface: {path:'metadata', revision?}; zenodo: {record_id}; "
        "cellxgene: {collection_id} or {disease, tissue, assay}; massive: {accession:'MSV000079514'}; "
        "synapse: {syn_id}; urls: {urls:[...]}."))] = None,
    project_code: Annotated[str | None, Field(description="Project sub-folder name. Default comes from the registry template (accession, study id, S3 prefix); required when the template cannot be filled (e.g. DepMap release '24Q4').")] = None,
    source: Annotated[str | None, Field(description="Source folder name; only for generic entries (open-urls/open-s3/open-hf/open-zenodo), e.g. 'GEO'.")] = None,
    levels: Annotated[list[Literal["raw", "processed", "metadata"]] | None, LEVELS_FIELD] = None,
    include: Annotated[list[str] | None, Field(description="Glob filters to keep, e.g. ['*.h5ad'] or ['*_MTG_*'].")] = None,
    exclude: Annotated[list[str] | None, Field(description="Glob filters to drop, e.g. ['*.raw'].")] = None,
    max_files: Annotated[int | None, Field(ge=1, description="Keep at most this many files (after filters).")] = None,
) -> str:
    """List what WOULD be downloaded (nothing is transferred) into <database>/<SOURCE>/<PROJECT_CODE>/
    {raw,processed,metadata}: file count and size per level, largest files, licence and access policy.
    Returns a plan_id for nas_submit_plan. Refuses 'forbidden' datasets (UK Biobank participant-level, GNPC)."""
    def go() -> dict:
        plan = planning.plan_dataset(cfg(), dataset_id, params, project_code, source, levels, include, exclude, max_files)
        out = plan.summary()
        out["dest_client"] = to_client(cfg(), plan.dest) if cfg().client_root else None
        return out
    return await _run(go)


@mcp.tool(name="nas_plan_urls", annotations=RO_NET)
async def nas_plan_urls(
    urls: Annotated[list, Field(description="URLs (http/https/ftp/sftp) or objects {url, name?, md5?|sha1?|sha256?, size?}.")],
    source: Annotated[str, Field(description="Source folder, e.g. 'GEO', 'HPA', 'DepMap', 'Web'.")],
    project_code: Annotated[str, Field(description="Project sub-folder, e.g. 'GSE157827' or '24Q4'.")],
    levels: Annotated[list[Literal["raw", "processed", "metadata"]] | None, LEVELS_FIELD] = None,
) -> str:
    """Plan a download of explicit URLs into <database>/<source>/<project_code>/ (open data only; the user is
    responsible for the licence)."""
    return await _run(lambda: planning.plan_urls(cfg(), urls, source, project_code, levels).summary())


@mcp.tool(name="nas_submit_plan", annotations=WRITE)
async def nas_submit_plan(
    plan_id: Annotated[str, Field(description="plan_id returned by nas_plan_dataset / nas_plan_urls.")],
    confirm_large: Annotated[bool, Field(description="Must be true for plans above the size threshold; only after the user agreed.")] = False,
    policy_ack: Annotated[str | None, Field(description="Required for summary_only / check_dua datasets: the user's own statement (e.g. DUA name/ID). Never invent it.")] = None,
) -> str:
    """Queue a plan on the NAS: checks free space (keeps a reserve), skips files already complete,
    hands each file to aria2 with its checksum (or starts the Synapse CLI). Downloads continue after
    this session ends."""
    return await _run(lambda: jobs.submit(cfg(), Plan.load(cfg(), plan_id), confirm_large, policy_ack))


# ------------------------------------------------------------------ jobs
@mcp.tool(name="nas_list_jobs", annotations=RO)
async def nas_list_jobs(limit: Annotated[int, Field(ge=1, le=100)] = 20) -> str:
    """Recent download jobs (newest first) with destination and planned size."""
    def go() -> list:
        return [{k: j.get(k) for k in ("job_id", "dataset_id", "dest", "kind", "bytes_planned", "policy")}
                for j in jobs.all_jobs(cfg())[:limit]]
    return await _run(go)


@mcp.tool(name="nas_job_status", annotations=RO)
async def nas_job_status(job_id: str) -> str:
    """Progress of a job: state, files by status, bytes done, speed, ETA, first errors with hints."""
    return await _run(jobs.status, cfg(), job_id)


@mcp.tool(name="nas_control_job",
          annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True, "openWorldHint": False})
async def nas_control_job(
    job_id: str,
    action: Literal["pause", "resume", "cancel"],
    purge_partial: Annotated[bool, Field(description="With cancel: delete INCOMPLETE files of this job (completed files are kept).")] = False,
) -> str:
    """Pause, resume or cancel a job. Cancel keeps partial files (resumable) unless purge_partial=true."""
    return await _run(jobs.control, cfg(), job_id, action, purge_partial)


@mcp.tool(name="nas_verify_job",
          annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
async def nas_verify_job(
    job_id: str,
    deep: Annotated[bool, Field(description="Re-hash every file with a known checksum (runs in the background; call again for the result).")] = False,
    restart: Annotated[bool, Field(description="With deep: discard a previous deep result and re-run.")] = False,
) -> str:
    """Verify a finished job (presence, no partial files, exact sizes; deep = checksums). On success writes
    PROVENANCE.md + files.tsv in the dataset folder and adds a row to CATALOG.tsv in the omics root."""
    if deep:
        return await _run(verify.start_deep, cfg(), job_id, restart)
    return await _run(verify.run, cfg(), job_id, False)


# ------------------------------------------------------------------ metadata & catalog
PROJECT_FIELD = Field(description="Project as 'SOURCE/PROJECT_CODE' (e.g. 'PRIDE/PXD046444'), or its full path "
                                  "(Mac path like /Volumes/AI4Sci/database/PRIDE/PXD046444 is accepted).")


@mcp.tool(name="nas_extract_metadata",
          annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True})
async def nas_extract_metadata(project: Annotated[str, PROJECT_FIELD]) -> str:
    """Deterministic first pass: build a draft standard metadata record (metadata/study.draft.json) and a samples
    table (samples.draft.tsv from PDC biospecimens, SDRF files or CELLxGENE datasets) from the saved source
    records and files on disk. Returns the draft plus 'gaps' = standard fields still empty."""
    return await _run(msvc.extract_draft, cfg(), project)


@mcp.tool(name="nas_inspect_files", annotations=RO)
async def nas_inspect_files(
    project: Annotated[str, PROJECT_FIELD],
    max_files: Annotated[int, Field(ge=1, le=200)] = 30,
) -> str:
    """Peek inside a project's metadata/processed files: table headers and categorical values, SDRF
    characteristics, h5ad obs columns/categories, parquet schema, mzTab metadata, zip listings; plus a
    per-level inventory. Use it to fill metadata gaps from file content."""
    return await _run(msvc.inspect_files, cfg(), project, max_files)


@mcp.tool(name="nas_lookup_ontology", annotations=RO_NET)
async def nas_lookup_ontology(
    terms: Annotated[list[dict], Field(description="[{field, text}], field in organism, tissue, sample_type, cell_type, cell_line, disease, sex, development_stage, ancestry, technology, software, perturbation.")],
    rows: Annotated[int, Field(ge=1, le=10)] = 3,
) -> str:
    """Normalise free text to ontology terms (MONDO, UBERON, CL, NCBITaxon, EFO, PATO, HsapDv, HANCESTRO, MS,
    ChEBI) via EBI OLS4. Returns ranked candidates {label, id, exact}; choose one or keep label-only."""
    return await _run(msvc.lookup_terms, terms, None, rows)


@mcp.tool(name="nas_save_metadata",
          annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
async def nas_save_metadata(
    project: Annotated[str, PROJECT_FIELD],
    study: Annotated[dict, Field(description="Full ADMS v1.0 study record (start from the draft). Every added/changed field needs curation.field_evidence[<section.field>] = {source, detail, confidence}.")],
    samples: Annotated[list[dict] | None, Field(description="Sample rows using the standard columns (sample_id required). Omit to keep the draft samples table.")] = None,
    status: Annotated[Literal["curated", "reviewed"], Field(description="'reviewed' only after the user checked it.")] = "curated",
) -> str:
    """Validate against the schema and write metadata/study.json (+ samples.tsv), then update the database
    index and CATALOG.tsv. Nothing is written if validation fails; errors are returned."""
    return await _run(msvc.save, cfg(), project, study, samples, True, status)


@mcp.tool(name="nas_query_catalog", annotations=RO)
async def nas_query_catalog(
    text: Annotated[str, Field(description="Free-text words matched anywhere in the study record.")] = "",
    organism: str | None = None, disease: str | None = None, tissue: str | None = None,
    sample_type: str | None = None, cell_type: str | None = None, technology: str | None = None,
    modality: Annotated[str | None, Field(description="e.g. ms_proteomics, affinity_proteomics, scRNA-seq")] = None,
    source: str | None = None,
    status: Annotated[Literal["draft", "curated", "reviewed"] | None, Field()] = None,
    limit: Annotated[int, Field(ge=1, le=500)] = 50,
) -> str:
    """Search the local database of downloaded studies by metadata (label substring or ontology id, e.g.
    disease='MONDO:0004975' or disease='alzheimer'). Returns paths as seen from the Mac and the NAS."""
    filters = {"organism": organism, "disease": disease, "tissue": tissue, "sample_type": sample_type,
               "cell_type": cell_type, "technology": technology, "modality": modality, "source": source, "status": status}
    return await _run(mindex.query, cfg(), text, filters, limit)


@mcp.tool(name="nas_rebuild_catalog",
          annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
async def nas_rebuild_catalog() -> str:
    """Rebuild _catalog/catalog.sqlite and CATALOG.tsv from every study.json / study.draft.json on disk."""
    return await _run(mindex.rebuild, cfg())


# ------------------------------------------------------------------ local ingest
@mcp.tool(name="nas_plan_ingest_local", annotations={**RO, "idempotentHint": False})
async def nas_plan_ingest_local(
    path: Annotated[str, Field(description="Existing folder or file on the NAS (inside allowed roots; Mac paths accepted).")],
    source: Annotated[str, Field(description="Source folder, e.g. 'ADNI', 'GEO', 'Lab'.")],
    project_code: Annotated[str, Field(description="Project sub-folder, e.g. 'ADNI3-CSF-proteomics'.")],
    mode: Literal["move", "copy"] = "move",
    dataset_id: Annotated[str | None, Field(description="Registry id if the data comes from a registered source (applies its access policy).")] = None,
    level: Annotated[Literal["raw", "processed", "metadata"] | None, Field(description="Force one level for all files; default auto-classifies.")] = None,
) -> str:
    """Dry run: show how an existing folder would be organised into <database>/<SOURCE>/<PROJECT>/{raw,processed,
    metadata} (counts, sizes, examples, conflicts). Nothing is moved until nas_apply_ingest."""
    return await _run(ingest.plan_ingest, cfg(), path, source, project_code, mode, dataset_id, level)


@mcp.tool(name="nas_apply_ingest", annotations=WRITE)
async def nas_apply_ingest(
    ingest_id: str,
    confirm: Annotated[bool, Field(description="Must be true, only after the user approved the plan.")] = False,
    policy_ack: Annotated[str | None, Field(description="Required when the registry policy is check_dua/summary_only.")] = None,
) -> str:
    """Execute an ingest plan (move = same-filesystem rename, copy = duplicate; never overwrites), write
    files.tsv and draft metadata."""
    return await _run(ingest.apply_ingest, cfg(), ingest_id, confirm, policy_ack)


@mcp.tool(name="nas_downloader_health", annotations=RO)
async def nas_downloader_health() -> str:
    """Check that the aria2 download engine is reachable; returns version and global speed/queue stats."""
    def go() -> dict:
        c = jobs.aria2_client(cfg())
        return {"aria2": c.version().get("version"), "global": c.global_stat(),
                "omics_root": str(cfg().omics_root), "registry": str(cfg().registry_path)}
    return await _run(go)


def check() -> int:
    """`nas-mcp --check`: validate config, registry, destination and aria2 before wiring up Claude Code."""
    import sys
    ok = True
    try:
        c = cfg()
        print(f"config    OK  {c.source_path}")
        print(f"registry  OK  {len(registry.load(c))} datasets ({c.registry_path})")
        for r in c.allowed_roots:
            w = r.is_dir() and os.access(r, os.W_OK)
            ok &= w
            print(f"root      {'OK ' if w else 'ERR'} {r} {'' if w else '(missing or not writable)'}")
        v = jobs.aria2_client(c).version()
        print(f"aria2     OK  version {v.get('version')} at {c.aria2_url}")
    except NasError as e:
        ok = False
        print(f"ERROR     {e}", file=sys.stderr)
    return 0 if ok else 1


def main() -> None:
    import sys
    if "--check" in sys.argv[1:]:
        raise SystemExit(check())
    mcp.run()


if __name__ == "__main__":
    main()
