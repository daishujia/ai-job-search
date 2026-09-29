"""Configuration loaded from YAML (default ~/.config/nas-mcp/config.yaml, or $NAS_MCP_CONFIG)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import NasError

DEFAULT_PATH = Path("~/.config/nas-mcp/config.yaml")


def _p(value: str | os.PathLike) -> Path:
    return Path(os.path.expandvars(str(value))).expanduser()


def _read_secret(path: Path | None) -> str | None:
    if path and path.is_file():
        return path.read_text().strip() or None
    return None


@dataclass
class Config:
    omics_root: Path
    allowed_roots: list[Path]
    registry_path: Path
    state_dir: Path
    aria2_url: str = "http://127.0.0.1:6800/jsonrpc"
    aria2_secret_file: Path | None = None
    hf_token_file: Path | None = None
    reserve_pct: float = 5.0
    confirm_above_gb: float = 100.0
    connections_per_file: int = 8
    max_plan_files: int = 200_000
    extra: dict = field(default_factory=dict)
    source_path: Path | None = None

    @property
    def aria2_secret(self) -> str | None:
        return _read_secret(self.aria2_secret_file)

    @property
    def hf_token(self) -> str | None:
        return _read_secret(self.hf_token_file) or os.environ.get("HF_TOKEN")

    @property
    def plans_dir(self) -> Path:
        return self.state_dir / "plans"

    @property
    def jobs_dir(self) -> Path:
        return self.state_dir / "jobs"

    @property
    def logs_dir(self) -> Path:
        return self.state_dir / "logs"

    def ensure_dirs(self) -> None:
        for d in (self.plans_dir, self.jobs_dir, self.logs_dir):
            d.mkdir(parents=True, exist_ok=True)


def load_config(path: str | os.PathLike | None = None) -> Config:
    cfg_path = _p(path or os.environ.get("NAS_MCP_CONFIG") or DEFAULT_PATH)
    if not cfg_path.is_file():
        raise NasError(
            f"Config not found at {cfg_path}. Run deploy/install_nas.sh on the NAS, "
            "or set NAS_MCP_CONFIG to a config.yaml (see deploy/config.example.yaml)."
        )
    raw = yaml.safe_load(cfg_path.read_text()) or {}
    try:
        omics_root = _p(raw["omics_root"])
    except KeyError as e:
        raise NasError(f"config.yaml is missing required key: {e}") from None
    allowed = [_p(r) for r in raw.get("allowed_roots", [])] or [omics_root]
    if omics_root not in allowed:
        allowed.append(omics_root)
    aria2 = raw.get("aria2", {}) or {}
    tokens = raw.get("tokens", {}) or {}
    cfg = Config(
        omics_root=omics_root,
        allowed_roots=allowed,
        registry_path=_p(raw.get("registry", cfg_path.parent / "registry.yaml")),
        state_dir=_p(raw.get("state_dir", "~/.local/state/nas-mcp")),
        aria2_url=aria2.get("url", "http://127.0.0.1:6800/jsonrpc"),
        aria2_secret_file=_p(aria2["secret_file"]) if aria2.get("secret_file") else None,
        hf_token_file=_p(tokens["huggingface_file"]) if tokens.get("huggingface_file") else None,
        reserve_pct=float(raw.get("free_space_reserve_pct", 5)),
        confirm_above_gb=float(raw.get("confirm_above_gb", 100)),
        connections_per_file=int(raw.get("connections_per_file", 8)),
        max_plan_files=int(raw.get("max_plan_files", 200_000)),
        extra={k: v for k, v in raw.items() if k not in {
            "omics_root", "allowed_roots", "registry", "state_dir", "aria2", "tokens",
            "free_space_reserve_pct", "confirm_above_gb", "connections_per_file", "max_plan_files"}},
    )
    cfg.source_path = cfg_path
    cfg.ensure_dirs()
    return cfg
