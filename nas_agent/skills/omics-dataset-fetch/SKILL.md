---
name: omics-dataset-fetch
description: Download public or DUA-governed omics datasets onto the home NAS (fnOS) with access-policy checks, size preflight, resumable aria2 transfers, checksum verification and provenance notes. Covers CPTAC/PDC, PRIDE/ProteomeXchange (PXD), MassIVE (MSV), UKB-PPP pQTL summary stats, AMP-AD (Synapse), CELLxGENE, SEA-AD, Allen Brain Cell Atlas, HCA, Tahoe-100M, JUMP Cell Painting, scPerturb, DepMap. Use when the user says "download/get/pull/save <dataset or accession> to the NAS", mentions PXD/MSV/PDC/syn accessions, or asks for single-cell, perturbation, Olink/SomaScan, AD/PD proteomics data on the NAS.
---

# omics-dataset-fetch

Needs the `nas` MCP server (tools prefixed `nas_`). Downloads run **on the NAS** and keep
going after this session ends. Nothing is transferred until `nas_submit_plan`.

Everything lands in `/Volumes/AI4Sci/database/<SOURCE>/<PROJECT_CODE>/{raw,processed,metadata}` (see the
dataset-ingest skill). The registry sets SOURCE and the default PROJECT_CODE (accession, study ID,
S3 prefix). Pass `project_code` only when the tool asks for it (e.g. a DepMap release) or the user
wants a different one.

## Workflow

1. **Find the dataset.** Run `nas_catalog_search` with keywords, such as `"alzheimer single cell"`,
   `"olink"` or `"cptac"`. Map accessions to registry ids:
   - `PXD…` → `pride`; single-cell MS proteomics → `sc-proteomics`
   - `MSV…` → `massive`
   - `PDC0…` → `cptac-pdc`
   - `syn…` → `amp-ad`, or `ukb-ppp-pqtl` for syn51365301
   - a CELLxGENE collection or a disease/tissue query → `cellxgene-discover`
   - any other open S3 bucket, Hugging Face repo, Zenodo record or URL list → `open-s3`, `open-hf`,
     `open-zenodo` or `open-urls`

   If the source isn't covered, say so. Propose a registry entry (with the provider's official access
   docs) instead of improvising.

2. **Respect the access policy** shown in the search result:
   - `forbidden` (UK Biobank participant-level Olink, GNPC): don't try. Explain that analysis happens
     inside UKB-RAP or the AD Workbench, and that only summary results may be exported.
   - `check_dua` (AMP-AD, AMP-PD/PPMI, ADNI): before submitting, ask the user whether:
     - they hold an active approval,
     - the DUA/DUC allows copies on a personal NAS,
     - the approval is theirs personally, not their employer's.

     Pass their answer verbatim as `policy_ack`. **Never invent or paraphrase an acknowledgement.**
     If any answer is no or unsure, stop.
   - `summary_only` (UKB-PPP pQTL): the `policy_ack` must state that only summary statistics are
     downloaded.
   - `allowed`: proceed, and mention the licence from the plan.

3. **Scope before you plan.** For big sources:
   - S3 sources: use `nas_browse_source` to walk sub-folders, e.g. SEA-AD `MTG/`, then pass
     `params.prefix`.
   - `cptac-pdc`: use `nas_browse_source` to see the data categories and their sizes.

   Prefer the smallest useful subset:
   - processed tables (`Protein Assembly`) before `Raw Mass Spectra`
   - JUMP profiles, not images (images run to hundreds of TB)
   - a tissue or disease slice of CELLxGENE, not the whole census
   - `include` globs such as `["*.h5ad"]` or `["*DLPFC*"]`

4. **Plan.** Call `nas_plan_dataset(dataset_id, params, project_code?, levels?, include?, exclude?,
   max_files?)`.
   - `levels=["processed"]` fetches results only; `["raw"]` fetches instrument files. Metadata files
     always come along.
   - Show the user:
     - file count and size per level
     - the largest files
     - the destination (`dest_client`, the Mac path)
     - licence and policy
     - whether sizes are only estimates (PRIDE)

   Ask them to confirm. Use `nas_storage_overview` if free space looks tight.

5. **Submit.** Call `nas_submit_plan(plan_id, confirm_large?, policy_ack?)`.
   - Set `confirm_large=true` only after the user explicitly agreed to a download above the threshold
     (default 100 GB).
   - Report the job id and the destination.
   - Jobs over ~20 GB: offer a check-in in about an hour (e.g. `send_later`) rather than polling.

6. **Track.** Use `nas_job_status(job_id)` and relay its `hint` on errors:
   - code 32 (checksum): cancel with `purge_partial`, then re-plan.
   - HTTP 4xx on PDC (expired signed URLs): re-plan and submit again; finished files are skipped.
   - code 8 (server can't resume): cancel with purge, then resubmit.

   Retry once. Report persistent failures instead of looping.

7. **Verify and document.** When the job is complete:
   - Run `nas_verify_job(job_id)`: presence, no partial files, exact sizes. This writes
     `PROVENANCE.md` and `files.tsv`, and drafts standard metadata (`metadata/study.draft.json`,
     `samples.draft.tsv`), which appears in `CATALOG.tsv` as `draft`.
   - Then run the **study-metadata-curation** skill to fill the reported gaps.
   - For a final integrity check, run `nas_verify_job(job_id, deep=true)` (background re-hash), then
     call it again later to read the result.
   - Tell the user where the data is, its size, the verification result and how to cite it.

## Parameters per connector (`params`)
| dataset_id | params |
|---|---|
| `pride`, `sc-proteomics` | `accession` (PXD), optional `categories` e.g. `["RAW","RESULT","SEARCH","PEAK","FASTA"]` |
| `cptac-pdc` | `pdc_study_id`, `data_categories` (browse first) |
| `massive` | `accession` (MSV), optional `subdir` |
| `sea-ad`, `abc-atlas`, `cellxgene-census`, `jump-cellpainting`, `open-s3` | `prefix` (+ `bucket`, `region` for open-s3) |
| `tahoe-100m`, `open-hf` | `path` (sub-folder), optional `revision` (+ `repo` for open-hf) |
| `cellxgene-discover` | `collection_id` or filters `disease` / `tissue` / `assay` / `organism` / `cell_type`; `filetype` H5AD or RDS |
| `scperturb`, `open-zenodo` | `record_id` (scPerturb default 13350497; ATAC 7058382) |
| `amp-ad`, `ukb-ppp-pqtl` | `syn_id` (needs the user's Synapse token on the NAS; sizes unknown up front) |
| `hpa-blood`, `hca`, `depmap`, `open-urls` | `urls`: list of URLs or `{url, name, md5/sha1/sha256, size}`; also pass `project_code` (and `source` for open-urls, e.g. `GEO`) |

Credentials (Synapse token, Hugging Face token) are set up by the user on the NAS. Never ask for a
token in chat.
