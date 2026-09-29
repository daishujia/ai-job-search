import os

import pytest

from nas_mcp import NasError, registry
from nas_mcp.paths import resolve_dest, safe_relpath


def test_relative_dest_goes_under_omics_root(cfg):
    assert resolve_dest(cfg, "proteomics/x") == (cfg.omics_root / "proteomics/x").resolve()


@pytest.mark.parametrize("bad", ["../../etc", "/etc/passwd", "proteomics/../../../root"])
def test_dest_outside_allowlist_rejected(cfg, bad):
    with pytest.raises(NasError, match="outside the allowed roots"):
        resolve_dest(cfg, bad)


def test_symlink_escape_rejected(cfg, tmp_path):
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    os.symlink(outside, cfg.omics_root / "link")
    with pytest.raises(NasError):
        resolve_dest(cfg, "link/sub")


@pytest.mark.parametrize("raw,ok", [("a/b.raw", "a/b.raw"), ("/abs/x", "abs/x"), ("a\\b", "a/b"), ("./a//b", "a/b")])
def test_safe_relpath_normalises(raw, ok):
    assert str(safe_relpath(raw)) == ok


@pytest.mark.parametrize("raw", ["../x", "a/../../x", "", "/"])
def test_safe_relpath_rejects(raw):
    with pytest.raises(NasError):
        safe_relpath(raw)


@pytest.mark.parametrize("ds", ["ukb-ppp-individual", "gnpc"])
def test_forbidden_datasets_refused(cfg, ds):
    with pytest.raises(NasError, match="Nothing was queued"):
        registry.gate(registry.get(cfg, ds))


def test_platform_only_and_manual_refused(cfg):
    with pytest.raises(NasError, match="provider's platform"):
        registry.gate(registry.get(cfg, "amp-pd"))
    with pytest.raises(NasError, match="manually"):
        registry.gate(registry.get(cfg, "adni"))


def test_locked_params(cfg):
    e = registry.get(cfg, "sea-ad")
    assert registry.merge_params(e, {"prefix": "MTG/"})["bucket"] == "sea-ad-single-cell-profiling"
    with pytest.raises(NasError, match="fixed"):
        registry.merge_params(e, {"bucket": "someone-elses-bucket"})


def test_ack_required_for_dua_and_summary(cfg):
    for pol in ("check_dua", "summary_only"):
        with pytest.raises(NasError, match="policy_ack"):
            registry.check_ack(pol, None)
    registry.check_ack("check_dua", "AMP-AD DUC syn9890650, personal approval")
    registry.check_ack("allowed", None)


def test_unknown_dataset_suggests(cfg):
    with pytest.raises(NasError, match="nas_catalog_search"):
        registry.get(cfg, "nope")


def test_search(cfg):
    ids = {r["id"] for r in registry.search(cfg, "alzheimer")}
    assert {"sea-ad", "amp-ad"} <= ids
