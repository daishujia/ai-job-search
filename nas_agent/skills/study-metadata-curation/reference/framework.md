# ADMS v1.0: AI4Sci Dataset Metadata Standard (field guide)

The machine-readable schema is `nas_mcp/metadata/study.schema.json`; `nas_save_metadata` validates
against it. Each project folder holds:

```
<SOURCE>/<PROJECT_CODE>/
  raw/ processed/ metadata/
  metadata/study.json        # curated record (study.draft.json = automatic first pass)
  metadata/samples.tsv       # one row per sample/aliquot (samples.draft.tsv = automatic)
  metadata/source/*.json     # untouched API records (PRIDE project, PDC study + biospecimens, CELLxGENE collection…)
  PROVENANCE.md  files.tsv
```

## 1. Sections
| Section | Key fields | Notes |
|---|---|---|
| `identity` | source, project_code, accessions[], title, description, version, doi, license, access_policy, dua_reference, publications[{pmid, doi, title, citation}], contacts[{name, affiliation, role}], consortium, keywords, urls | No personal emails. `access_policy` comes from the registry. |
| `biology` | organism, tissue, sample_type, cell_type, cell_line, disease, sex, development_stage, ancestry (all term lists), perturbations[{type, agent(term), dose, duration}] | Terms are `{label, id?, ontology?, verbatim?}` |
| `assay` | modality[] (enum), technology (terms), acquisition[], quantification[], fractions[], feature_type, software (terms), protocol_summary | See §4 for modality choice |
| `design` | study_type, n_subjects, n_samples, n_cells, n_features, groups[{name, n, description}], factors[], timepoints[] | Counts must come from a source; don't estimate |
| `data` | levels.{raw,processed,metadata}.{files, bytes, formats}, nas_path, client_path, verified | Filled by the tools |
| `curation` | status (draft/curated/reviewed), field_evidence{"section.field": {source, detail, confidence}}, needs_review[], notes | Required |
| `extensions` | free-form per source (`pride`, `cellxgene`, …) | Not indexed |

## 2. Ontologies (same choices as the CELLxGENE schema and SDRF-Proteomics)
| Field | Ontology | Examples |
|---|---|---|
| organism | NCBITaxon | Homo sapiens NCBITaxon:9606 · Mus musculus NCBITaxon:10090 |
| tissue | UBERON | dorsolateral prefrontal cortex UBERON:0009834 · kidney UBERON:0002113 |
| sample_type | UBERON (biofluids), else free label | blood plasma UBERON:0001969 · blood serum UBERON:0001977 · cerebrospinal fluid UBERON:0001359; "tumor tissue", "cell line" as labels |
| cell_type | CL | astrocyte CL:0000127 |
| disease | MONDO (EFO if absent); healthy = PATO:0000461 "normal" | Alzheimer disease MONDO:0004975 · Parkinson disease MONDO:0005180 |
| sex | PATO | female PATO:0000383 · male PATO:0000384 |
| development_stage | HsapDv / MmusDv | |
| ancestry | HANCESTRO | |
| technology | MS (mass spectrometers), EFO (sequencing/assays) | Orbitrap Astral MS:1003378 · 10x 3' v3 EFO:0009922; Olink Explore 3072 and SomaScan 7k as labels unless OLS has an exact term |
| cell_line | Cellosaurus (CVCL_xxxx) / CLO | |
| perturbation agent | ChEBI (compounds), HGNC symbols as labels (genes) | |

Placeholder IDs such as `unknown` or `na` are never stored; use a label-only term or leave the field
empty.

## 3. samples.tsv standard columns (in order)
`sample_id` (required), `subject_id`, `organism`, `organism_id`, `tissue`, `tissue_id`, `sample_type`,
`disease`, `disease_id`, `sex`, `age`, `age_unit`, `development_stage`, `cell_type`, `cell_line`,
`condition`, `treatment`, `timepoint`, `batch`, `replicate`, `label`, `data_file`.

Other source columns are kept after these as `char:<name>` or `comment:<name>`, following SDRF's
characteristics[] and comment[].

Mapping cheatsheet:
- **SDRF:** `source name` → sample_id; `characteristics[organism part]` → tissue;
  `characteristics[individual]` → subject_id; `factor value[x]` → condition; `comment[label]` → label;
  `comment[data file]` → data_file.
- **PDC biospecimens:** aliquot_submitter_id → sample_id; case_submitter_id → subject_id;
  sample_type (Primary Tumor / Solid Tissue Normal) → sample_type.
- **h5ad obs (CELLxGENE schema):** donor_id → subject_id; `*_ontology_term_id` → the *_id columns;
  one row per donor×sample, not per cell.
- **Olink / SomaScan tables:** SampleID → sample_id. Plate/well go to `char:` columns, and NPX/RFU
  units go in `assay.quantification`.

## 4. Choosing `assay.modality`
- **ms_proteomics:** LC-MS/MS DDA or DIA, TMT, label-free, PRM/SRM. Add `phosphoproteomics` for
  enriched fractions and `single_cell_proteomics` for SCoPE2/plexDIA.
- **affinity_proteomics:** Olink (PEA; NPX), SomaScan (aptamer; RFU), NULISA, antibody arrays.
- **scRNA-seq vs snRNA-seq:** decided by suspension type (cell vs nucleus). Use `multiome` for joint
  RNA+ATAC, and `spatial_transcriptomics` for Visium, MERFISH, Xenium or Slide-seq.
- **gwas_summary_statistics:** pQTL/GWAS summary statistics (e.g. UKB-PPP).
- **imaging_phenotypic:** Cell Painting and other high-content imaging profiles.

## 5. Evidence confidence
- **high:** a verbatim structured field (API or SDRF), or an explicit statement in the paper's
  Methods or Tables.
- **medium:** derived from file content (h5ad categories, table headers), or a normalisation that
  isn't an exact ontology match.
- **low:** inferred from title or abstract wording. Always list these in `needs_review`.

## 6. Minimal curated example (CPTAC CCRCC proteome, abbreviated)
```json
{"schema_version": "1.0",
 "identity": {"source": "CPTAC-PDC", "project_code": "PDC000127", "title": "CPTAC CCRCC Discovery Study - Proteome",
              "accessions": ["PDC000127"], "access_policy": "allowed", "consortium": "Clinical Proteomic Tumor Analysis Consortium"},
 "biology": {"organism": [{"label": "Homo sapiens", "id": "NCBITaxon:9606"}],
             "disease": [{"label": "clear cell renal carcinoma", "id": "MONDO:0005005", "verbatim": "Clear Cell Renal Cell Carcinoma"},
                         {"label": "normal", "id": "PATO:0000461", "verbatim": "Solid Tissue Normal"}],
             "tissue": [{"label": "kidney", "id": "UBERON:0002113"}],
             "sample_type": [{"label": "tumor tissue", "verbatim": "Primary Tumor"}, {"label": "normal adjacent tissue", "verbatim": "Solid Tissue Normal"}]},
 "assay": {"modality": ["ms_proteomics"], "quantification": ["TMT10"], "fractions": ["Proteome"], "feature_type": "protein"},
 "design": {"study_type": "case-control", "n_subjects": 124, "n_samples": 208},
 "curation": {"status": "curated", "field_evidence": {
     "biology.disease": {"source": "api", "detail": "PDC study disease_type + biospecimen sample_type; MONDO via OLS exact", "confidence": "high"},
     "design.study_type": {"source": "inferred", "detail": "tumor vs normal adjacent tissue pairs", "confidence": "medium"}},
   "needs_review": ["design.study_type"]}}
```
