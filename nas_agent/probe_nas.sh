#!/usr/bin/env bash
# probe_nas.sh - READ-ONLY inventory of an fnOS (Debian 12) NAS for agent/MCP planning.
# Changes nothing. Safe to run as a normal user; a few sections show more if sudo works without a password.
#
# Run from a computer on the same Wi-Fi:
#   ssh <user>@192.168.86.28 'bash -s' < probe_nas.sh > nas_probe.txt
# Then share nas_probe.txt (review it first - it lists usernames, folders and listening ports).

section() { printf '\n===== %s =====\n' "$1"; }
have()    { command -v "$1" >/dev/null 2>&1; }
run()     { "$@" 2>&1 || true; }
SUDO=""; sudo -n true 2>/dev/null && SUDO="sudo -n"

section "IDENTITY"
echo "date: $(date -Is)"; echo "host: $(hostname)"; echo "user: $(id)"
echo "passwordless sudo: $([ -n "$SUDO" ] && echo yes || echo no)"

section "OS / KERNEL / fnOS"
run cat /etc/os-release
run uname -a
for f in /etc/fnos-release /etc/trim-release /usr/trim/etc/version; do [ -r "$f" ] && { echo "--- $f"; cat "$f"; }; done
ls -d /usr/trim 2>/dev/null && echo "(fnOS 'trim' system dir present)"
have systemctl && systemctl list-units --type=service --no-pager --no-legend 2>/dev/null | grep -iE 'trim|fn|docker|smb|nfs|ssh|aria|qbit|transmission' | head -40

section "HARDWARE"
run nproc; run free -h
grep -m1 'model name' /proc/cpuinfo 2>/dev/null
for n in /sys/class/net/*; do i=$(basename "$n"); [ "$i" = lo ] && continue
  echo "nic $i: state=$(cat "$n/operstate" 2>/dev/null) speed=$(cat "$n/speed" 2>/dev/null)Mb/s"; done

section "DISKS / STORAGE POOLS"
run lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL
df -hT 2>/dev/null | grep -E '^Filesystem|/vol|/$'
run cat /proc/mdstat
have btrfs && $SUDO btrfs filesystem show 2>/dev/null | head -30
have smartctl && [ -n "$SUDO" ] && for d in $(lsblk -dno NAME,TYPE | awk '$2=="disk"{print $1}'); do
  echo "--- SMART /dev/$d"; $SUDO smartctl -H -A "/dev/$d" 2>/dev/null | grep -E 'result|Temperature|Reallocated|Pending|Power_On' ; done

section "VOLUME LAYOUT (depth 2, dirs only)"
for v in /vol*; do [ -d "$v" ] || continue; echo "--- $v"
  find "$v" -mindepth 1 -maxdepth 2 -type d 2>/dev/null | grep -vE '/(@|\.)' | head -60
  echo "writable by me: $([ -w "$v" ] && echo yes || echo no)"; done
echo "--- home: $HOME (writable: $([ -w "$HOME" ] && echo yes || echo no))"

section "SSH"
grep -hEi '^\s*(Port|PermitRootLogin|PasswordAuthentication|PubkeyAuthentication|AllowUsers|AllowGroups)' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null
ls -la ~/.ssh 2>/dev/null

section "LISTENING PORTS"
have ss && run ss -tlnH | awk '{print $4}' | sort -u

section "DOCKER"
if have docker; then
  run docker version --format 'client {{.Client.Version}} / server {{.Server.Version}}'
  docker info >/dev/null 2>&1 && D=docker || D="$SUDO docker"
  echo "docker usable as me: $(docker info >/dev/null 2>&1 && echo yes || echo no)"
  run $D info --format 'root dir: {{.DockerRootDir}}  storage: {{.Driver}}'
  run $D ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
  have docker && run docker compose version
else echo "docker: not found"; fi

section "RUNTIMES"
for t in python3 pip3 node npm uv pipx git; do printf '%-8s ' "$t"; have "$t" && ("$t" --version 2>&1 | head -1) || echo "-"; done
have python3 && python3 -c 'import venv, ssl, sys; print("venv+ssl ok, python", sys.version.split()[0])' 2>&1

section "TRANSFER / DOWNLOAD TOOLS"
for t in aria2c curl wget rsync rclone lftp ascp prefetch fasterq-dump qbittorrent-nox transmission-daemon tmux screen sha256sum md5sum pigz zstd; do
  printf '%-20s %s\n' "$t" "$(command -v "$t" || echo -)"; done

section "OUTBOUND INTERNET (HEAD requests only)"
for u in https://www.ebi.ac.uk https://ftp.pride.ebi.ac.uk https://ftp.ncbi.nlm.nih.gov https://pypi.org https://registry-1.docker.io/v2/; do
  have curl && printf '%-40s %s\n' "$u" "$(curl -sI -o /dev/null -m 8 -w '%{http_code} %{time_total}s' "$u" 2>/dev/null || echo fail)"; done

section "DONE"
