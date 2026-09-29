#!/usr/bin/env bash
# Copy nas_agent/ to the NAS and run the installer there, from your laptop (macOS/Linux/WSL/Git Bash).
#   nas_agent/deploy/deploy_from_laptop.sh <you>@192.168.86.28 --share AI4Sci [installer options]
set -euo pipefail
TARGET="${1:?usage: $0 user@nas-ip --share AI4Sci | --omics-root PATH  [--client-root /Volumes/AI4Sci/database] [--allow PATH] [--with-synapse] [--install-uv] [--no-docker]}"; shift
HERE="$(cd "$(dirname "$0")/.." && pwd)"   # .../nas_agent

echo "==> Checking key-based SSH to $TARGET"
ssh -o BatchMode=yes -o ConnectTimeout=8 "$TARGET" true || {
  echo "Key login failed. Set it up once:  ssh-keygen -t ed25519 && ssh-copy-id $TARGET" >&2; exit 1; }

echo "==> Uploading code to ~/nas-mcp/src"
tar -C "$HERE" --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.egg-info' -czf - server datasets deploy skills probe_nas.sh \
  | ssh "$TARGET" 'mkdir -p ~/nas-mcp/src && tar -xzf - -C ~/nas-mcp/src'

echo "==> Running installer on the NAS"
ssh -t "$TARGET" "bash ~/nas-mcp/src/deploy/install_nas.sh $(printf '%q ' "$@")"
