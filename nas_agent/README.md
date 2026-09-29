# NAS Agent Toolkit — fnOS @ 192.168.86.28

Design for Claude Code **skills** + an **MCP server** that let an agent inspect NAS storage and
submit large download jobs into a chosen NAS folder. Status: **design + probe script**; the
server is built after `probe_nas.sh` results confirm what the NAS has installed.

## 0. Why a probe first
The NAS is on a private home LAN (`192.168.86.28`), unreachable from cloud sessions. Discovery
must run from a machine on the same Wi-Fi:

```bash
# 1. fnOS web UI (http://192.168.86.28:5666) → Settings → SSH → enable (off by default)
# 2. From a laptop on the same Wi-Fi:
ssh <admin-user>@192.168.86.28 'bash -s' < nas_agent/probe_nas.sh > nas_probe.txt
```
The probe is read-only: OS/fnOS version, disks and RAID/Btrfs, `/volN` layout, SSH config,
listening ports, Docker, Python, transfer tools (aria2c/rsync/rclone/ascp/sra-tools) and outbound reach
to EBI/PRIDE/NCBI/PyPI/Docker Hub.

Known fnOS facts it confirms: Debian 12 base; storage spaces mount at `/vol1`, `/vol2`…;
web UI on 5666; Docker data root typically `/vol1/docker`.

## 1. Architecture (recommended)

```
Claude Code (laptop: Desktop app or `claude remote-control`)
        │  MCP over stdio, tunnelled through SSH (key auth, no new open ports)
        ▼
nas-mcp  (Python, runs ON the NAS as unprivileged user `agent`)
        │  JSON-RPC on 127.0.0.1:6800 (rpc-secret)
        ▼
aria2 daemon (Docker container, restart=always)  ──► /vol1/<share>/<selected folder>
```

Design choices:
- **Jobs run on the NAS, not the laptop.** A 200 GB download survives the laptop sleeping and
  Claude sessions ending. The agent only submits and checks jobs.
- **aria2** as the engine: resumable, multi-connection HTTP/FTP/SFTP, BitTorrent/Metalink,
  built-in checksum checks, and a JSON-RPC API. Running it in Docker keeps fnOS system updates
  from wiping apt-installed packages.
- **stdio over SSH** (`ssh agent@nas python server.py`): nothing listens on the LAN except SSH.
  Registered with:
  `claude mcp add nas -- ssh agent@192.168.86.28 /home/agent/nas-mcp/.venv/bin/python /home/agent/nas-mcp/server.py`
- **Least privilege.** Create a dedicated fnOS user `agent` with write access only to the target
  shares (for example, `/vol1/1000/Downloads` and `/vol1/1000/Datasets`). Don't give it root or admin rights.

## 2. MCP server — `nas-mcp` tool surface

| Tool | Purpose | Guardrails |
|---|---|---|
| `storage_overview()` | Capacity/free/used per `/volN`, RAID/Btrfs state | read-only |
| `list_folders(path, depth=1)` | Browse allowed roots so the user can pick a destination | allowlisted roots only; `realpath` check blocks `..`/symlink escape |
| `folder_usage(path)` | Size + file count of a folder, largest children | read-only, timeout |
| `create_folder(path)` | Make a destination folder | inside allowlist; no overwrite |
| `preflight_download(urls, dest)` | HEAD each URL → size, resumability, filename; compare to free space | refuses if size > free − reserve (for example 5%) |
| `submit_download(urls, dest, checksum?, connections=8, label?)` | Queue in aria2 (`aria2.addUri` with `dir`), return job id | runs preflight first; ask for confirmation above a size threshold |
| `submit_manifest(manifest_path \| rows, dest)` | Bulk-queue a TSV/JSON list (url, subpath, md5/sha256) | same checks per row; one batch id |
| `job_status(id?)` / `list_jobs(state)` | Progress, speed, ETA, errors | read-only |
| `pause_job` / `resume_job` / `cancel_job(id)` | Control | cancel keeps partial file unless `purge=true` |
| `verify_files(dest, checksums)` | Post-download md5/sha256 check → report | read-only |
| `job_log(since)` | Append-only JSONL audit (`~/.nas-mcp/jobs.jsonl`) | — |

Deliberately **not** exposed: delete/move of existing data, sudo, arbitrary shell. Add those only
behind an explicit confirm flag if ever needed.

MCP **resources**: `nas://volumes`, `nas://jobs/active`. MCP **prompt**: `download-to-nas`.

## 3. Claude Code skills (layered on the MCP tools)

| Skill | Trigger | Workflow |
|---|---|---|
| **`nas-download`** | "download X to the NAS", "save this dataset to …" | resolve folder (list → user picks or confirm) → `preflight` → show size/ETA/free space → `submit` → `send_later` check-in → `verify_files` → summary |
| **`nas-storage`** | "how full is the NAS", "what's using space" | `storage_overview` + `folder_usage` → ranked report, warn at >80% |
| **`omics-dataset-fetch`** | "get PXD0xxxxx", "pull CPTAC / SEA-AD / Tahoe-100M…" | registry lookup → **access-policy gate** → manifest + size preflight → `submit_manifest` → verify checksums → `PROVENANCE.md` + `CATALOG.tsv`. Spec: `skills/omics-dataset-fetch/SKILL.md` |
| **`nas-health`** | "check the NAS", weekly routine | SMART, RAID/Btrfs state, temps, Docker container health (read-only) |
| **`nas-upload`** (optional) | "push these results to the NAS" | `rsync -aP --partial` from laptop to a chosen folder over SSH |

`omics-dataset-fetch` is where this becomes a real research tool. MS raw-file datasets are often
100 GB–1 TB, and resumable, checksum-verified NAS-side downloads with provenance notes are what
make them reusable later.

## 3b. Dataset coverage and access tiers
`datasets/registry.yaml` lists 19 sources. Each has a `local_download` policy that the skill enforces:

| Tier | Sources | What reaches the NAS |
|---|---|---|
| **allowed** (open) | CPTAC/PDC, PRIDE, MassIVE, HPA, CELLxGENE Census, SEA-AD, Allen Brain Cell Atlas, HCA, single-cell MS proteomics, Tahoe-100M, JUMP Cell Painting, scPerturb, DepMap | Full files (filtered to a sensible subset) |
| **summary_only** | UKB-PPP pQTL summary stats (Synapse syn51365301) | Summary statistics + metadata |
| **check_dua** | AMP-AD Knowledge Portal, AMP-PD (incl. PPMI Olink/SomaScan), ADNI | Only after the user confirms the DUA allows copies on a personal device |
| **forbidden** | UK Biobank participant-level Olink (UKB-RAP), GNPC SomaScan (AD Workbench) | Nothing. Analysis stays in the enclave; only exported summary results |

Additional connectors this needs in `nas-mcp` (run in one "fetcher" Docker image on the NAS):
`fetch_s3(prefix, include)` (aws CLI, no-sign-request) · `fetch_synapse(syn_id)` (synapseclient)
· `fetch_hf(repo, allow_patterns)` (huggingface-cli) · `fetch_pdc(study_id, file_types)` (PDC
GraphQL) · `fetch_pride(accession, patterns)` · `catalog_search(query)` (reads the registry).

## 4. Build plan (after the probe)
1. **Foundation:** enable SSH; create `agent` user + SSH key; choose allowlisted roots; start aria2
   container bound to `127.0.0.1:6800` with an `rpc-secret`.
2. **Core:** `nas-mcp/server.py` (Python `mcp` SDK, venv on NAS) with the tools above + unit
   tests for path-guarding and preflight; register via `claude mcp add`.
3. **Output:** `SKILL.md` files for `nas-download`, `nas-storage`, `omics-dataset-fetch`;
   end-to-end test: small file → large file (resume after container restart) → checksum verify.

## 5. Security notes
- Don't port-forward 5666, 22 or 6800 to the internet. For remote access, use a VPN (for example, Tailscale or WireGuard).
- aria2 RPC listens on localhost only and always uses `rpc-secret`.
- Treat URLs and manifests as untrusted input. The server validates schemes (http/https/ftp/sftp/magnet)
  and never passes them to a shell.
