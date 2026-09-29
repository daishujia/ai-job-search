---
name: nas-download
description: Send large file downloads (any URL list, public S3 prefix, Hugging Face repo or Zenodo record) to a chosen folder on the home NAS, where they run resumably in the background via aria2, then track, pause/resume/cancel and verify them. Use for "download this to the NAS", "save these files on my NAS", "is my NAS download done", "pause/cancel the NAS download". For named omics datasets prefer the omics-dataset-fetch skill.
---

# nas-download

Needs the `nas` MCP server.

1. **Destination.** Everything goes to `/Volumes/AI4Sci/database/<SOURCE>/<PROJECT_CODE>/`, with
   files sorted into `raw/`, `processed/` and `metadata/`.
   - Ask for, or derive, the source (e.g. `GEO`, `Zenodo`, `Lab`) and a project code (the source's
     accession where there is one).
   - `nas_list_folders` shows what exists.
2. **Plan.** Use `nas_plan_urls(urls, source, project_code, levels?)` for plain links, adding `md5`,
   `sha1` or `sha256` when the source publishes them. For a bucket, repo or record, use `nas_plan_dataset` with `open-s3`,
   `open-hf` or `open-zenodo`. Show the file count, size and destination, and confirm with the user.
   Only use these generic entries for data the user is entitled to download. The licence is their call,
   and the plan records it in the provenance file.
3. **Submit.** `nas_submit_plan(plan_id)`. Set `confirm_large=true` only after explicit agreement above
   the size threshold. The tool refuses plans that would eat into the free-space reserve. If it does,
   suggest narrowing the plan or freeing space (`nas_folder_usage`).
4. **Track and control.**
   - Progress: `nas_job_status`. `nas_list_jobs` finds earlier jobs.
   - `nas_control_job` with `pause` / `resume` / `cancel`. Only add `purge_partial=true` when the user
     wants the incomplete files deleted; completed files are never removed.
   - If aria2 is unreachable, run `nas_downloader_health` and relay the start command it suggests.
5. **Finish.** Run `nas_verify_job` and report the folder, size and result.
