---
name: study-metadata-curation
description: Extract, standardize and save study- and sample-level metadata for datasets stored in the AI4Sci database on the NAS (/Volumes/AI4Sci/database/<SOURCE>/<PROJECT_CODE>). Uses the ADMS v1.0 schema with CELLxGENE/SDRF ontologies (NCBITaxon, UBERON, CL, MONDO, EFO, PATO, HsapDv, HANCESTRO, MS) and records evidence for every field. Use for "curate/extract/standardize the metadata of <study>", "fill in the metadata", "what samples/disease/tissue is in <project>", after a dataset download finishes, or when CATALOG.tsv shows metadata_status=draft.
---

# study-metadata-curation

Needs the `nas` MCP server. The field guide is `reference/framework.md`; read it before your first
curation in a session.

## Principles
- **Evidence or nothing.** Every value you add or change gets
  `curation.field_evidence["<section>.<field>"] = {source, detail, confidence}`.
  - `source` is one of: `api`, `file`, `publication`, `repository_page`, `inferred`, `user`.
  - Never invent sample counts, diseases, ages or ontology IDs.
  - If something is unknown, leave it empty and add it to `curation.needs_review`.
- **Keep the source's words.** When you normalise a label, put the original text in `verbatim`.
- **Deterministic first, reasoning second.** Tools extract; you fill the gaps and resolve conflicts.
- **Don't overwrite curated work silently.** If `metadata/study.json` already exists with status
  `curated` or `reviewed`, show a diff of your proposed changes and ask before saving.

## Workflow
1. **Draft.** `nas_extract_metadata(project)`.
   - `project` is `SOURCE/PROJECT_CODE`, or the Mac path `/Volumes/AI4Sci/database/...`.
   - This writes `metadata/study.draft.json` and `samples.draft.tsv`, and returns `gaps`.
   - Verification runs this automatically after each download, so a draft may already exist.
2. **Read the files.** `nas_inspect_files(project)` returns:
   - SDRF characteristics
   - table headers and their categorical values (group/disease columns)
   - h5ad `obs` columns and categories (donor, disease, tissue, cell type, sex, age)
   - mzTab metadata
   - the file inventory per level

   Use these to fill `biology.*`, `design.groups`, `n_samples`, `n_cells` and `n_features`.
3. **Read the publication.**
   - For PMIDs/DOIs in `identity.publications`, use the PubMed tools if available
     (`get_article_metadata`, `get_full_text_article`), otherwise the DOI landing page.
   - Extract: study type, cohort sizes per group, sample type (plasma/serum/CSF/tissue), disease
     definitions, platform details (Olink panel, SomaScan version, TMT plex, DIA window scheme),
     and timepoints.
   - Use `source: "publication"` with the section as detail (e.g. "Methods: Patient cohorts").
4. **Normalise terms.**
   - Send every new free-text biology or technology label to `nas_lookup_ontology` as
     `[{field, text}]`.
   - Accept an `exact` candidate. Otherwise choose the closest candidate only if the definition
     clearly matches; else keep the label without an `id`.
   - Healthy controls use `normal` (`PATO:0000461`) in `biology.disease`, next to the disease terms.
5. **Samples table.**
   - Keep the draft rows (SDRF, PDC biospecimens or CELLxGENE datasets) unless they're wrong.
   - If you build rows from a table or h5ad, use the standard columns (reference §3).
   - Pass `samples` only when you changed them; otherwise the draft is kept.
6. **Save.** `nas_save_metadata(project, study, samples?, status="curated")`.
   - If it returns `schema_errors`, fix those fields and call again; nothing is written until the
     record validates.
   - Use `status="reviewed"` only after the user has looked at the summary.
7. **Report.** Give the user:
   - a compact summary: title, modality, organism, disease, tissue/sample type, platform, n
   - what came from the API, the files or the publication
   - the remaining `needs_review` items and the path of `study.json`

## Batch mode
Use "curate all drafts" when asked:
- `nas_query_catalog(status="draft")`, then run the workflow per project.
- Keep going when one project fails.
- Report a table of saved, needs-review and failed projects at the end.
