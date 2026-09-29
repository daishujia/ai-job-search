---
name: omics-dataset-fetch
description: Fetch public or DUA-governed omics datasets (CPTAC/PDC, PRIDE, MassIVE, UKB-PPP pQTL summary stats, AMP-AD, ADNI, CELLxGENE, SEA-AD, Allen Brain Cell Atlas, HCA, Tahoe-100M, JUMP Cell Painting, scPerturb, DepMap) onto the home NAS into a chosen folder, with access-policy checks, size preflight, checksum verification and provenance notes. Triggers on "download dataset to NAS", "get PXD…", "pull CPTAC", "fetch SEA-AD", "save Tahoe-100M", "UKB-PPP", "GNPC", "AMP-PD", "single-cell atlas to NAS".
---

# omics-dataset-fetch

Requires the `nas` MCP server (see `nas_agent/README.md`). The source of truth is
`nas_agent/datasets/registry.yaml`.

## 1. Resolve the request
- Map the request to a registry `id` (or to an accession: `PXD…` → pride, `MSV…` → massive,
  `PDC0…` → cptac-pdc, `syn…` → synapse-backed entry).
- If the user named something that isn't in the registry, look up its official access route
  (provider docs, not third-party mirrors) and propose a new registry entry before downloading.
- If the entry has no `verified` date, or it is older than 6 months, re-check the provider's
  access page first.

## 2. Enforce `local_download` (never skip)
| value | action |
|---|---|
| `forbidden` | Do **not** queue anything. Explain that analysis must happen in the provider's enclave (UKB-RAP, AD Workbench), and offer to set up in-platform analysis or download only exported summary results. |
| `summary_only` | Queue only summary-statistic/metadata files. Refuse participant-level files. |
| `check_dua` | Ask the user to confirm that (a) they hold an active approval, (b) the DUA/DUC allows copies on this personal device, and (c) the approval is personal, not institutional/employer-held. Record the DUA name/ID in PROVENANCE.md. If any answer is no or unsure, stop. |
| `allowed` | Proceed; still honour the dataset licence (note it in PROVENANCE.md). |

Credentials (Synapse PAT, HF token) live only on the NAS in `~agent/.config/` (mode 600). Never
ask the user to paste tokens into chat.

## 3. Scope and preflight
1. Build a file manifest with the entry's connector (PDC manifest, PRIDE file list, `aws s3 ls
   --no-sign-request --recursive`, `synapse` listing, HF file list).
2. Show the user the file count, total size, and a suggested filter. Large sets default to the
   smallest useful subset: processed tables before raw; the relevant tissue/disease slice of
   CELLxGENE; JUMP profiles, not images.
3. Destination = `<omics root>/<nas_path>`. Confirm the folder with the user or pick it from `list_folders`.
4. `preflight_download` → refuse if the size exceeds free space minus 5% reserve. Ask for
   explicit confirmation above 100 GB.

## 4. Submit and track
- `submit_manifest(rows, dest)` (aria2 for HTTP/FTP; the fetcher container for s3/synapse/hf).
- Schedule a check-in (`send_later`, ~1 h for >50 GB). On each check: `job_status`; retry failed
  items once, and report persistent failures rather than looping.

## 5. Verify and document
- `verify_files` against provider checksums (PRIDE/PDC md5, S3 ETag where single-part,
  Synapse md5). Report mismatches and re-queue only those files.
- Write `PROVENANCE.md` in the dataset folder: source URL/accession, version/release,
  download date, file count/size, checksum result, licence or DUA reference, citation.
- Append the dataset to `<omics root>/CATALOG.tsv` (id, path, size, date, access tier).

## Suggested NAS layout
```
<omics root>/
  proteomics/{cptac,pride,massive,single-cell}/
  affinity/{ukb-ppp-pqtl,hpa}/
  neuro/{amp-ad,amp-pd,adni}/
  singlecell/{cellxgene,sea-ad,abc-atlas,hca}/
  phenotypic/{tahoe-100m,cellpainting,scperturb,depmap}/
  CATALOG.tsv
```
