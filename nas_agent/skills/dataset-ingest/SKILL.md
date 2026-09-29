---
name: dataset-ingest
description: Ingest public omics datasets (raw and/or processed) into the AI4Sci database on the NAS at /Volumes/AI4Sci/database/<SOURCE>/<PROJECT_CODE>/{raw,processed,metadata}, from a remote repository or from files already on the NAS (manual downloads such as ADNI/LONI exports, GEO supplementary files, older folders), then produce standardized metadata. Use for "ingest", "add this dataset to the database", "organize these downloads", "file this folder under ADNI", "bring GSE… into the database".
---

# dataset-ingest

Needs the `nas` MCP server. The layout is fixed:

```
/Volumes/AI4Sci/database/                 (NAS: <share path>/database)
  <SOURCE>/<PROJECT_CODE>/
     raw/        instrument/sequencer output: .raw .d .wiff .mzML .mgf .fastq .bam images
     processed/  results: quant tables, search outputs, matrices, .h5ad .rds .parquet .mzTab
     metadata/   SDRF, README, clinical/sample sheets, source API records, study.json, samples.tsv
     PROVENANCE.md  files.tsv
  CATALOG.tsv  _catalog/ (catalog.sqlite, downloads.tsv)
```

`SOURCE` is the database or consortium (PRIDE, MassIVE, CPTAC-PDC, CELLxGENE, SEA-AD, Tahoe, JUMP-CellPainting,
UKB-PPP, AMP-AD, ADNI, GEO, …).

`PROJECT_CODE` is that source's own identifier (PXD…, MSV…, PDC…, syn…, a CELLxGENE collection ID,
GSE…, an S3 region prefix, or a release such as `24Q4`).

Use the registry defaults. Only invent a code when the source has none; then keep it short and
stable, and tell the user.

## A. Remote dataset (raw or processed)
Use the **omics-dataset-fetch** skill: `nas_plan_dataset` → confirm → `nas_submit_plan` → track →
`nas_verify_job`.

- Pick `levels` from what the user wants:
  - `["processed"]` for analysis-ready tables or h5ad
  - `["raw"]` or no filter for re-processing
- Metadata files always come along.
- Verification drafts the metadata automatically. Continue with section C.

## B. Files already on the NAS
1. `nas_plan_ingest_local(path, source, project_code, mode="move", dataset_id?)`. This is a dry run.
   - Mac paths are accepted.
   - Pass `dataset_id` when the data comes from a registered source (e.g. `adni`, `amp-ad`) so its
     access policy applies. Forbidden sources are refused.
2. Show the user: from → to, file count and size per level, conflicts, and the mode.
   - `move` is an instant rename on the same volume.
   - Use `copy` when the plan says the files are on a different filesystem, or when the user wants to
     keep the originals.
3. After they agree, call `nas_apply_ingest(ingest_id, confirm=true, policy_ack?)`.
   - `check_dua` sources need the user's own statement that their DUA allows the local copy.
   - Existing files are never overwritten.
4. If the auto-classification put something in the wrong level (e.g. a clinical CSV in `processed`),
   re-plan that file or subfolder with `level="metadata"`.

## C. Metadata (always finish with this)
Run the **study-metadata-curation** skill on `SOURCE/PROJECT_CODE`. A dataset counts as ingested
when `metadata/study.json` exists with status `curated` and shows up in
`nas_query_catalog(source=…)`.

## Checks before reporting done
- `nas_query_catalog(source=SOURCE)` lists the project with the expected sizes.
- No `.aria2` partial files remain; `nas_verify_job` returns `result: ok`.
- Tell the user the Mac path, what's in raw, processed and metadata, and any `needs_review` items.
