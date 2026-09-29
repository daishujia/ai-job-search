# NAS Agent Toolkit: AI4Sci omics database on the fnOS NAS

Claude Code skills and an MCP server (`nas-mcp`) that build and maintain a local omics database on
the NAS (fnOS, Debian 12, `192.168.86.28`):
- **Download** public datasets (raw and/or processed) resumably on the NAS via aria2.
- **Organize** everything as `/Volumes/AI4Sci/database/<SOURCE>/<PROJECT_CODE>/{raw,processed,metadata}`.
- **Ingest** data already on the NAS, such as manual ADNI/GEO downloads.
- **Extract and standardize** study- and sample-level metadata (ADMS v1.0), indexed and searchable.

```
Claude Code (Mac) ──stdio over SSH──► nas-mcp (Python, on the NAS)
                                        ├─ connectors: PRIDE · PDC/CPTAC · S3 open data · Hugging Face · Zenodo
                                        │              CELLxGENE · MassIVE · Synapse · URL lists · local folders
                                        ├─ registry.yaml → access policy + SOURCE/PROJECT_CODE naming
                                        ├─ aria2 (127.0.0.1, secret) ─► <share>/database/<SOURCE>/<PROJECT>/…
                                        └─ metadata: extract → inspect → ontology (OLS4) → validate → SQLite index
Mac Finder: /Volumes/AI4Sci/database/…   (same folder over SMB; every tool accepts Mac paths)
```

## Database layout
```
/Volumes/AI4Sci/database/                    NAS: /vol1/<uid>/AI4Sci/database (found by the installer)
├── CATALOG.tsv                              one row per project: organism, disease, tissue, n, sizes, status, path
├── _catalog/catalog.sqlite, downloads.tsv   search index (nas_query_catalog) + download log
├── PRIDE/PXD046444/
│   ├── raw/         .raw .d .wiff .mzML .mgf .fastq .bam images           (instrument/sequencer output)
│   ├── processed/   search results, quant tables, matrices, .h5ad .parquet .mzTab
│   ├── metadata/    study.json · samples.tsv · SDRF · README · source/<api records>.json
│   ├── PROVENANCE.md   source, version, licence/DUA, verification, citation
│   └── files.tsv       per-file size, checksum, source URL
├── CPTAC-PDC/PDC000127/   CELLxGENE/<collection_id>/   SEA-AD/MTG/   Tahoe/Tahoe-100M/
├── UKB-PPP/syn51365301/   AMP-AD/syn…/   ADNI/<your code>/   GEO/GSE…/   DepMap/24Q4/ …
```
`SOURCE` and the default `PROJECT_CODE` come from `datasets/registry.yaml` (accession, study ID, S3
prefix, release). Files are sorted into levels by per-source rules (PRIDE file categories, PDC data
categories), with file extensions and names as the fallback.

## Metadata standard (ADMS v1.0)
- **Schema:** `server/src/nas_mcp/metadata/study.schema.json` (JSON Schema 2020-12). Sections:
  `identity`, `biology`, `assay`, `design`, `data`, `curation` (evidence per field), `extensions`.
- **Ontologies:** the CELLxGENE-schema / SDRF-Proteomics choices: NCBITaxon, UBERON, CL, MONDO, EFO,
  PATO, HsapDv, HANCESTRO, MS, ChEBI, Cellosaurus. Lookups go through EBI OLS4.
- **Samples:** `metadata/samples.tsv` uses standard columns (`sample_id`, `subject_id`, organism,
  tissue, sample_type, disease, sex, age, condition, label, data_file, …). Source extras are kept as
  `char:` / `comment:` columns.
- **Field guide:** `skills/study-metadata-curation/reference/framework.md`.
- **Automatic first pass:** every verified download or ingest produces a draft from the saved API
  records and files on disk:
  - PRIDE project CV terms and SDRF samples
  - PDC study details and biospecimens
  - CELLxGENE ontology terms
  - Zenodo, Hugging Face and MassIVE records

  Claude then fills the gaps (from file content and publications), normalizes terms and saves a
  validated `study.json`.

## Setup (about 15 minutes, once)
1. **fnOS:** SSH is already on. Decide which account runs the service. Using the account that owns
   the `AI4Sci` folder means files show up as yours on the Mac. Set up key login from the Mac:
   `ssh-copy-id <you>@192.168.86.28`.
2. **Deploy** from the Mac (the NAS path of `AI4Sci` is auto-detected):
   ```bash
   nas_agent/deploy/deploy_from_laptop.sh <you>@192.168.86.28 --share AI4Sci --with-synapse \
       [--allow /vol1/1000/Downloads] [--install-uv] [--no-docker]
   ```
   - It writes `~/.config/nas-mcp/config.yaml` with `omics_root: <share>/database` and
     `client_root: /Volumes/AI4Sci/database`.
   - It installs the Python venv, including h5py and pyarrow for file inspection.
   - It generates the aria2 engine config.
   - Re-running upgrades the code and keeps your config.
3. **Start aria2**, then run the self-check (the installer prints the exact commands):
   ```bash
   ssh -t <you>@192.168.86.28 'sudo docker compose -f ~/nas-mcp/aria2/docker-compose.yml up -d --build'
   ssh <you>@192.168.86.28 '~/nas-mcp/.venv/bin/nas-mcp --check'
   ```
4. **Connect Claude Code and install the skills** on the Mac:
   ```bash
   claude mcp add nas --scope user -- ssh -o BatchMode=yes <you>@192.168.86.28 <printed path>/nas-mcp
   nas_agent/deploy/install_skills.sh
   ```
5. **Credentials** (stay on the NAS):
   - `synapse config` for AMP-AD and UKB-PPP.
   - `~/.config/nas-mcp/hf.token` for gated Hugging Face repos.

## Skills
| Skill | For |
|---|---|
| `omics-dataset-fetch` | "Download PXD046444 processed files", "get CPTAC PDC000127 protein tables", "pull SEA-AD MTG h5ad" |
| `dataset-ingest` | The end-to-end pipeline: remote or local data into the layout, then metadata. "File ~/Downloads/ADNI_export under ADNI" |
| `study-metadata-curation` | Extract, standardize and save metadata with evidence; batch-curate every draft |
| `nas-download` | Any URL list, bucket or record into `<SOURCE>/<PROJECT_CODE>` |
| `nas-storage` | Capacity, what's using space, search the database (`nas_query_catalog`) |

## MCP tools (22)
| Group | Tools |
|---|---|
| Storage | `nas_storage_overview`, `nas_list_folders`, `nas_folder_usage`, `nas_create_folder` |
| Find and plan | `nas_catalog_search` (registry), `nas_browse_source`, `nas_plan_dataset` (`project_code`, `levels`), `nas_plan_urls` |
| Download | `nas_submit_plan`, `nas_list_jobs`, `nas_job_status`, `nas_control_job`, `nas_verify_job`, `nas_downloader_health` |
| Local ingest | `nas_plan_ingest_local` (dry run), `nas_apply_ingest` (move/copy, never overwrites) |
| Metadata | `nas_extract_metadata`, `nas_inspect_files`, `nas_lookup_ontology`, `nas_save_metadata` (schema-validated) |
| Database | `nas_query_catalog` (label or ontology-ID search), `nas_rebuild_catalog` |

### Access policies (enforced in code)
| Policy | Sources | Behaviour |
|---|---|---|
| `allowed` | CPTAC/PDC, PRIDE, MassIVE, HPA, CELLxGENE, SEA-AD, Allen ABC Atlas, HCA, Tahoe-100M, JUMP, scPerturb, DepMap, generic open data | Plan → confirm → download |
| `summary_only` | UKB-PPP pQTL summary statistics | Requires `policy_ack` |
| `check_dua` | AMP-AD, AMP-PD/PPMI, ADNI (local ingest) | Requires your own DUA statement, recorded in PROVENANCE and `study.json` |
| `forbidden` | UK Biobank participant-level Olink, GNPC | Refused for download *and* local ingest |

**Guards:**
- Path allowlist, with symlinks resolved; Mac paths are mapped to NAS paths.
- Remote names are sanitized, and the free-space reserve and large-download confirmation always apply.
- No delete tool. Ingest never overwrites; moves only within one filesystem.
- aria2 RPC on localhost with a secret; tokens never written to plans.

## Development and tests
```bash
cd nas_agent/server && uv venv && uv pip install -e '.[test,inspect]'
pytest                               # 67 tests: unit, metadata, ingest, real-aria2 e2e, MCP stdio protocol
NAS_MCP_LIVE=1 pytest -m live        # 10 live tests against PRIDE, PDC, S3, HF, CELLxGENE, Zenodo, OLS4
```

**Verified in the build environment:**
- The test suite passes on MCP SDK 2.2.0 and 1.30.0.
- Live: real verified downloads from S3, Hugging Face and PRIDE. The real PXD046444 SDRF was
  downloaded and auto-extracted into 18 sample rows (6 samples).
- Live: PDC000127 extraction with 208 biospecimens; the SEA-AD CELLxGENE draft (>1M nuclei, MONDO
  and CL IDs); OLS4 term lookups.
- The installer found the `AI4Sci` share in a simulated `/vol*` tree, and `nas-mcp --check` passed.

**Not yet exercised:**
- The real fnOS box.
- Building the aria2 container (no Docker daemon here; the Compose file validates).
- MassIVE's FTP walk (fake-server tested).
- The Synapse CLI (needs your token).

## Known limits
- PDC signed URLs last about a week: re-plan and resubmit (finished files are skipped).
- PRIDE sizes are estimates. Integrity comes from PRIDE SHA-1 checksums (confirmed on a real file),
  enforced by aria2.
- S3 ETags are advisory (not MD5 for multipart or KMS-encrypted objects); deep verify reports
  `etag_differs`.
- Auto-classification into raw/processed/metadata is rule-based. Re-plan an ingest with
  `level=...` to correct a folder.
- Ontology IDs are only as good as the evidence. Low-confidence fields are listed in
  `curation.needs_review` for you to check.
