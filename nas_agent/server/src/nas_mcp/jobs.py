"""Turn a confirmed Plan into a running job (aria2 downloads or a detached process) and track it."""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

from . import NasError
from .aria2 import Aria2
from .config import Config
from .manifest import FileEntry, Plan, human
from .paths import ensure_inside, resolve_dest, safe_relpath
from .registry import check_ack

STATUS_KEYS = ["gid", "status", "totalLength", "completedLength", "downloadSpeed", "errorCode", "errorMessage"]


def aria2_client(cfg: Config) -> Aria2:
    return Aria2(cfg.aria2_url, cfg.aria2_secret)


# ---------------------------------------------------------------- persistence
def _job_path(cfg: Config, job_id: str) -> Path:
    if not job_id.isalnum():
        raise NasError("Invalid job_id.")
    return cfg.jobs_dir / f"{job_id}.json"


def load_job(cfg: Config, job_id: str) -> dict:
    p = _job_path(cfg, job_id)
    if not p.is_file():
        raise NasError(f"Unknown job_id {job_id}. See nas_list_jobs.")
    return json.loads(p.read_text())


def save_job(cfg: Config, job: dict) -> None:
    _job_path(cfg, job["job_id"]).write_text(json.dumps(job))


def all_jobs(cfg: Config) -> list[dict]:
    jobs = [json.loads(p.read_text()) for p in cfg.jobs_dir.glob("*.json")]
    return sorted(jobs, key=lambda j: j["created"], reverse=True)


# ---------------------------------------------------------------- helpers
def free_bytes(path: Path) -> tuple[int, int]:
    p = path
    while not p.exists():
        p = p.parent
    du = shutil.disk_usage(p)
    return du.free, du.total


def is_complete(target: Path, f: FileEntry) -> bool:
    if not target.is_file() or Path(str(target) + ".aria2").exists():
        return False
    return not (f.size_exact and f.size is not None and target.stat().st_size != f.size)


def _aria2_opts(cfg: Config, dest: Path, f: FileEntry) -> dict:
    rel = safe_relpath(f.relpath)
    target = ensure_inside(dest / rel, dest)
    opts = {
        "dir": str(target.parent), "out": target.name,
        "split": str(cfg.connections_per_file),
        "max-connection-per-server": str(min(cfg.connections_per_file, 16)),
        "continue": "true", "auto-file-renaming": "false", "allow-overwrite": "false",
    }
    if f.checksum and f.checksum_type and not f.attrs.get("advisory_checksum"):
        opts["checksum"] = f"{f.checksum_type}={f.checksum}"  # aria2 fails the file on mismatch
    if f.auth == "hf":
        if not cfg.hf_token:
            raise NasError("This dataset needs a Hugging Face token on the NAS (tokens.huggingface_file).")
        opts["header"] = [f"Authorization: Bearer {cfg.hf_token}"]
    return opts


# ---------------------------------------------------------------- submit
def submit(cfg: Config, plan: Plan, confirm_large: bool = False, policy_ack: str | None = None) -> dict:
    check_ack(plan.policy, policy_ack)
    dest = resolve_dest(cfg, plan.dest)
    free, total = free_bytes(dest)
    reserve = int(total * cfg.reserve_pct / 100)

    todo, skipped = [], []
    for f in plan.files:
        (skipped if is_complete(dest / safe_relpath(f.relpath), f) else todo).append(f)
    need = sum(f.size or 0 for f in todo)
    if need > free - reserve:
        raise NasError(
            f"Not enough space: need {human(need)}, free {human(free)} with a {cfg.reserve_pct:.0f}% reserve "
            f"({human(reserve)}). Narrow the plan (include/exclude/max_files) or free space first."
        )
    if need > cfg.confirm_above_gb * 1024**3 and not confirm_large:
        raise NasError(
            f"This plan downloads {human(need)} (> {cfg.confirm_above_gb:.0f} GB). Show the user the plan "
            "summary and call again with confirm_large=true only after they agree."
        )
    dest.mkdir(parents=True, exist_ok=True)
    job = {
        "job_id": plan.plan_id, "plan_id": plan.plan_id, "dataset_id": plan.dataset_id,
        "dest": str(dest), "kind": plan.kind, "policy": plan.policy, "policy_ack": policy_ack,
        "created": time.time(), "bytes_planned": need, "skipped_existing": [f.relpath for f in skipped],
        "gids": {}, "free_before": free,
    }
    if plan.kind == "process":
        _start_process(cfg, job, [c.replace("{dest}", str(dest)) for c in plan.command or []])
    else:
        client = aria2_client(cfg)
        calls = [("aria2.addUri", [[f.url], _aria2_opts(cfg, dest, f)]) for f in todo]
        results = client.multicall(calls) if calls else []
        failed = []
        for f, r in zip(todo, results):
            if isinstance(r, str):
                job["gids"][r] = f.relpath
            else:
                failed.append({"path": f.relpath, "error": (r or {}).get("faultString")})
        job["submit_errors"] = failed
    save_job(cfg, job)
    return {
        "job_id": job["job_id"], "dest": job["dest"], "queued": len(job["gids"]) if plan.kind == "aria2" else None,
        "skipped_existing": len(skipped), "bytes_to_download": human(need),
        "free_space_before": human(free), "submit_errors": job.get("submit_errors", [])[:10],
        "next": "Check progress with nas_job_status; when complete run nas_verify_job.",
    }


def _start_process(cfg: Config, job: dict, cmd: list[str]) -> None:
    log = cfg.logs_dir / f"{job['job_id']}.log"
    exitfile = cfg.jobs_dir / f"{job['job_id']}.exit"
    with open(log, "ab") as fh:
        p = subprocess.Popen([sys.executable, "-m", "nas_mcp.runner", str(exitfile), "--", *cmd],
                             cwd=job["dest"], stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT,
                             start_new_session=True)  # survives the MCP/SSH session ending
    job.update(pid=p.pid, log=str(log), exitfile=str(exitfile), command=cmd)


# ---------------------------------------------------------------- status
def _pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    try:  # zombie check
        return Path(f"/proc/{pid}/stat").read_text().split()[2] != "Z"
    except OSError:
        return True


def _dir_size(path: Path) -> int:
    total = 0
    for root, _, files in os.walk(path):
        for n in files:
            try:
                total += os.lstat(os.path.join(root, n)).st_size
            except OSError:
                pass
    return total


def status(cfg: Config, job_id: str, max_errors: int = 10) -> dict:
    job = load_job(cfg, job_id)
    dest = Path(job["dest"])
    if job["kind"] == "process":
        alive = _pid_alive(job.get("pid"))
        rc = Path(job["exitfile"]).read_text().strip() if Path(job["exitfile"]).exists() else None
        tail = Path(job["log"]).read_text(errors="replace")[-1500:] if Path(job["log"]).exists() else ""
        state = "running" if alive else ("complete" if rc == "0" else "error" if rc else "stopped")
        return {"job_id": job_id, "state": state, "exit_code": rc, "bytes_on_disk": human(_dir_size(dest)),
                "dest": str(dest), "log_tail": tail}

    gids = job["gids"]
    counts: dict[str, int] = {}
    done_b = total_b = speed = 0
    errors = []
    results = aria2_client(cfg).multicall([("aria2.tellStatus", [g, STATUS_KEYS]) for g in gids]) if gids else []
    for (gid, rel), r in zip(gids.items(), results):
        if not isinstance(r, dict) or "faultCode" in r:
            # aria2 forgot the gid (restart / result purge): fall back to the file on disk
            target = dest / safe_relpath(rel)
            st = "complete" if target.is_file() and not Path(str(target) + ".aria2").exists() else "unknown"
            counts[st] = counts.get(st, 0) + 1
            if st == "complete":
                sz = target.stat().st_size
                done_b += sz
                total_b += sz
            continue
        st = r["status"]
        counts[st] = counts.get(st, 0) + 1
        done_b += int(r.get("completedLength", 0))
        total_b += int(r.get("totalLength", 0))
        speed += int(r.get("downloadSpeed", 0))
        if st == "error" and len(errors) < max_errors:
            errors.append({"path": rel, "code": r.get("errorCode"), "message": r.get("errorMessage")})
    n = len(gids)
    active = counts.get("active", 0) + counts.get("waiting", 0)
    if n and counts.get("complete", 0) == n:
        state = "complete"
    elif active:
        state = "running"
    elif counts.get("paused"):
        state = "paused"
    elif counts.get("error") or counts.get("unknown"):
        state = "error"
    elif counts.get("removed"):
        state = "cancelled"
    else:
        state = "complete" if not n else "unknown"
    remaining = max(job.get("bytes_planned", 0), total_b) - done_b
    return {
        "job_id": job_id, "dataset_id": job["dataset_id"], "state": state, "dest": str(dest),
        "files": n, "by_status": counts, "skipped_existing": len(job.get("skipped_existing", [])),
        "downloaded": human(done_b), "of_known": human(max(total_b, job.get("bytes_planned", 0))),
        "percent": round(100 * done_b / total_b, 1) if total_b else None,
        "speed": human(speed) + "/s",
        "eta_minutes": round(remaining / speed / 60, 1) if speed else None,
        "errors": errors,
        "hint": _hint(errors),
    }


def _hint(errors: list[dict]) -> str:
    codes = {str(e.get("code")) for e in errors}
    tips = []
    if "32" in codes:
        tips.append("code 32 = checksum mismatch (corrupt or changed file): cancel with purge_partial and re-plan.")
    if "8" in codes:
        tips.append("code 8 = server cannot resume (no byte ranges): cancel with purge_partial and resubmit.")
    if codes & {"3", "22", "24"}:
        tips.append("HTTP 4xx: signed URLs may have expired (PDC) or access changed: re-plan and submit; "
                    "finished files are skipped.")
    if errors and not tips:
        tips.append("Network/server errors: resubmitting the same plan retries only unfinished files.")
    return " ".join(tips)


# ---------------------------------------------------------------- control
def control(cfg: Config, job_id: str, action: str, purge_partial: bool = False) -> dict:
    job = load_job(cfg, job_id)
    if job["kind"] == "process":
        if action != "cancel":
            raise NasError("Process jobs (Synapse) support cancel only; resubmitting resumes (synapse skips existing files).")
        if _pid_alive(job.get("pid")):
            os.killpg(job["pid"], signal.SIGTERM)
        return {"job_id": job_id, "cancelled": True}
    method = {"pause": "aria2.forcePause", "resume": "aria2.unpause", "cancel": "aria2.forceRemove"}[action]
    gids = list(job["gids"])
    res = aria2_client(cfg).multicall([(method, [g]) for g in gids]) if gids else []
    ok = sum(1 for r in res if isinstance(r, str))
    purged = 0
    if action == "cancel" and purge_partial:
        dest = Path(job["dest"])
        for rel in job["gids"].values():
            target = ensure_inside(dest / safe_relpath(rel), dest)
            ctl = Path(str(target) + ".aria2")
            if ctl.exists():  # only incomplete files (those with a control file) are removed
                for p in (target, ctl):
                    if p.exists():
                        p.unlink()
                        purged += 1
    return {"job_id": job_id, "action": action, "applied": ok, "not_applicable": len(gids) - ok,
            "purged_partial_files": purged}
