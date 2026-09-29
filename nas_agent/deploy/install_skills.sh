#!/usr/bin/env bash
# Install the NAS skills for Claude Code on this computer (user-level, available in every project).
set -euo pipefail
SRC="$(cd "$(dirname "$0")/../skills" && pwd)"; DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"
for d in "$SRC"/*/; do n=$(basename "$d"); rm -rf "${DEST:?}/$n"; cp -R "$d" "$DEST/$n"; echo "installed $n -> $DEST/$n"; done
