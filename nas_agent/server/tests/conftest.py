import json
import shutil
from pathlib import Path

import pytest
import yaml

from nas_mcp.config import load_config

REPO_REGISTRY = Path(__file__).resolve().parents[2] / "datasets" / "registry.yaml"


@pytest.fixture
def cfg(tmp_path):
    root = tmp_path / "vol1" / "omics"
    root.mkdir(parents=True)
    reg = tmp_path / "registry.yaml"
    shutil.copy(REPO_REGISTRY, reg)
    c = tmp_path / "config.yaml"
    c.write_text(yaml.safe_dump({
        "omics_root": str(root), "allowed_roots": [str(root)], "registry": str(reg),
        "state_dir": str(tmp_path / "state"), "confirm_above_gb": 1,
        "client_root": "/Volumes/AI4Sci/database",
    }))
    return load_config(c)


class FakeResp:
    def __init__(self, data, links=None):
        self._d, self.links = data, links or {}

    def json(self):
        return self._d


class FakeHttp:
    """Routes by URL substring -> canned JSON/text. Records calls."""

    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def _find(self, url, payload=None):
        self.calls.append((url, payload))
        key = url + (json.dumps(payload) if payload else "")
        for k, v in self.routes.items():
            if k in key:
                return v(url, payload) if callable(v) else v
        raise AssertionError(f"unrouted {url} {payload}")

    def get_json(self, url, params=None, headers=None):
        return self._find(url)

    def post_json(self, url, payload, headers=None):
        return self._find(url, payload)

    def get_text(self, url, params=None, headers=None):
        return self._find(url + "?" + "&".join(f"{k}={v}" for k, v in (params or {}).items()))

    def get_json_paged(self, url, params=None, headers=None, max_pages=1000):
        return self._find(url)
