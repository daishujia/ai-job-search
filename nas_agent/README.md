# NAS Agent Toolkit: omics dataset downloads to the fnOS NAS

Claude Code skills and an MCP server (`nas-mcp`) that plan, queue, track and verify large
public-omics downloads **on the NAS** (fnOS, Debian 12, `192.168.86.28`) into folders you choose.
Transfers run in an aria2 daemon, so they resume after interruptions and keep going after Claude
or the laptop goes to sleep.

```
Claude Code (laptop) ──stdio over SSH (key auth)──► nas-mcp (Python, NAS user `agent`)
                                                        ├─ connectors: PRIDE · PDC/CPTAC · S3 · Hugging Face · Zenodo
                                                        │              CELLxGENE · MassIVE · Synapse · URL lists
                                                        ├─ registry.yaml → access-policy gate
                                                        └─ aria2 JSON-RPC (127.0.0.1, secret) ─► /vol1/…/omics/<dataset>/
```

## Layout
| Path | What |
|---|---|
| `server/` | `nas-mcp` Python package (MCP SDK v1 and v2 compatible), tests |
| `datasets/registry.yaml` | 24 sources, each with an access policy, connector, defaults and target folder |
| `skills/` | Claude Code skills: `omics-dataset-fetch`, `nas-download`, `nas-storage` |
| `deploy/` | `deploy_from_laptop.sh`, `install_nas.sh`, aria2 container, `install_skills.sh`, example config |
| `probe_nas.sh` | Read-only NAS inventory (optional, for troubleshooting) |

## Setup (about 15 minutes, once)
Run from a laptop on the home Wi-Fi (macOS, Linux, or Windows via WSL/Git Bash).

1. **fnOS web UI** (`http://192.168.86.28:5666`):
   - Create a user such as `agent`. It doesn't need to be an admin.
   - Create or choose a shared folder for datasets (e.g. `omics` → `/vol1/1000/omics`) and give
     `agent` read/write.
   - SSH is already enabled.
2. **SSH key login.** The MCP connection can't type passwords.
   `ssh-keygen -t ed25519` (if you have no key), then `ssh-copy-id agent@192.168.86.28`.
3. **Deploy and install:**
   ```bash
   nas_agent/deploy/deploy_from_laptop.sh agent@192.168.86.28 --omics-root /vol1/1000/omics \
       [--allow /vol1/1000/Downloads] [--with-synapse] [--install-uv]
   ```
   - This uploads the code to `~/nas-mcp/src` and creates a venv.
   - It writes `~/.config/nas-mcp/config.yaml` and a random aria2 secret (mode 600).
   - It also generates the aria2 container files.
   - Re-running upgrades the code and keeps your config.
   - Add `--install-uv` if fnOS lacks `python3-venv`.
   - Add `--no-docker` to use a host `aria2c` via a systemd user service instead of the container.
4. **Start aria2 once** (the command is printed by the installer; `sudo` is needed unless `agent` is in
   the docker group):
   ```bash
   ssh -t agent@192.168.86.28 'sudo docker compose -f ~/nas-mcp/aria2/docker-compose.yml up -d --build'
   ssh agent@192.168.86.28 '~/nas-mcp/.venv/bin/nas-mcp --check'   # config / registry / folders / aria2
   ```
5. **Connect Claude Code and install the skills** on the laptop:
   ```bash
   claude mcp add nas --scope user -- ssh -o BatchMode=yes agent@192.168.86.28 /home/agent/nas-mcp/.venv/bin/nas-mcp
   nas_agent/deploy/install_skills.sh
   ```
   (Use the exact path printed by the installer.)
6. **Credentials** (only for sources that need them; they stay on the NAS):
   - Synapse (AMP-AD, UKB-PPP pQTL): as `agent`, run `~/nas-mcp/.venv/bin/synapse config` with a
     personal access token.
   - Gated Hugging Face repos: put a read token in `~/.config/nas-mcp/hf.token` (chmod 600).
   - PDC, PRIDE, S3 open data, Zenodo and CELLxGENE need no login.

## Using it
Ask Claude in plain language. The skills drive the tools:
- "Get the SEA-AD MTG snRNA-seq h5ad files onto the NAS"
- "Download CPTAC CCRCC PDC000127 protein tables"
- "Pull PXD046444 raw files into proteomics/benchmarks"
- "What Parkinson's single-cell datasets are on CELLxGENE, and how big?"
- "How full is the NAS?"
- "Is the Tahoe download done?"

Every download follows the same sequence:
1. Plan: list the files, total size, licence and policy. Nothing is downloaded yet.
2. You confirm.
3. Submit: free-space check, skip files already present, queue each file with its checksum.
4. Check status.
5. Verify: writes `PROVENANCE.md` and `files.tsv` in the dataset folder, and a row in
   `<omics root>/CATALOG.tsv`.

### MCP tools
| Tool | Purpose |
|---|---|
| `nas_storage_overview`, `nas_list_folders`, `nas_folder_usage`, `nas_create_folder` | Storage (allowlisted roots only; no delete tool exists) |
| `nas_catalog_search`, `nas_browse_source` | Find datasets; peek at S3 sub-folders / PDC data categories |
| `nas_plan_dataset`, `nas_plan_urls` | Build a plan (listing only) → `plan_id` |
| `nas_submit_plan` | Queue it. Enforces the free-space reserve, `confirm_large` (>100 GB) and `policy_ack` for DUA/summary-only sources |
| `nas_list_jobs`, `nas_job_status`, `nas_control_job` | Track, pause, resume, cancel (optionally purge partial files only) |
| `nas_verify_job` | Sizes and presence; `deep=true` re-hashes in the background; writes provenance |
| `nas_downloader_health` | aria2 reachability, version, queue stats |

### Access policies (from `registry.yaml`, enforced in code)
| Policy | Sources | Behaviour |
|---|---|---|
| `allowed` | CPTAC/PDC, PRIDE, MassIVE, HPA, CELLxGENE (census and per-dataset), SEA-AD, Allen Brain Cell Atlas, HCA, single-cell MS, Tahoe-100M, JUMP Cell Painting, scPerturb, DepMap, generic open S3/HF/Zenodo/URLs | Plan → confirm → download |
| `summary_only` | UKB-PPP pQTL summary stats (Synapse syn51365301) | Submit requires `policy_ack` |
| `check_dua` | AMP-AD (Synapse), AMP-PD/PPMI, ADNI | Submit requires your own DUA statement. AMP-PD and ADNI have no automated connector (Terra/BigQuery, LONI) |
| `forbidden` | UK Biobank participant-level Olink (UKB-RAP), GNPC SomaScan (AD Workbench) | Refused; analyse in the enclave |

Guards:
- Every path is resolved (symlinks included) and must sit inside `allowed_roots`.
- Remote file names are sanitised.
- aria2 RPC is bound to localhost and uses a secret.
- Tokens are never written to plan files.
- aria2's session folder is mode 700.

## Development and tests
```bash
cd nas_agent/server && uv venv && uv pip install -e '.[test]'
pytest                                       # unit + real-aria2 end-to-end (needs aria2c) + MCP stdio protocol
NAS_MCP_LIVE=1 pytest -m live                # real APIs + three small real downloads, checksum-verified
```

Tested in the build environment:
- 38 offline and end-to-end tests pass on MCP SDK 2.2.0 and 1.30.0, plus 7 live tests.
- Live listings: PRIDE, PDC, SEA-AD S3, Tahoe-100M, CELLxGENE, scPerturb/Zenodo.
- Real verified downloads: SEA-AD S3 (MD5), Hugging Face (SHA-256) and PRIDE over HTTPS.
- The installer runs in both Docker and no-Docker modes, and `nas-mcp --check` passes.

**Not yet exercised:**
- Running on the actual fnOS box.
- Building the aria2 container (no Docker daemon was available; the Compose file validates).
- MassIVE's FTP walk (no FTP access; unit-tested with a fake server).
- The Synapse CLI path (needs your token).

## Known limits
- PDC signed URLs last about a week. If a PDC job stalls with HTTP 4xx, re-plan and submit again;
  finished files are skipped.
- PRIDE sizes are estimates. Integrity comes from PRIDE's SHA-1 checksums, which aria2 checks
  (confirmed against a real 23 MB PXD046444 file).
- S3 ETags equal the file's MD5 only for some objects (never for multipart or KMS-encrypted ones), so
  they are advisory: they never fail a download, and deep verify reports `etag_differs` as a note.
- Synapse jobs run the `synapse` CLI in the background. Total size isn't known up front, so only the
  free-space reserve applies.
- Browsing is limited to what each source's API exposes; CELLxGENE filtering matches labels
  (disease / tissue / assay / organism / cell_type).
