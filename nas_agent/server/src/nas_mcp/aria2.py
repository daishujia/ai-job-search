"""Minimal aria2 JSON-RPC client."""
from __future__ import annotations

import itertools
from typing import Any

import httpx

from . import NasError

_ids = itertools.count(1)


class Aria2:
    def __init__(self, url: str, secret: str | None, timeout: float = 30.0):
        self.url, self.secret = url, secret
        self.client = httpx.Client(timeout=timeout, trust_env=False)  # localhost only, never via proxy

    def _params(self, params: list) -> list:
        return ([f"token:{self.secret}"] if self.secret else []) + list(params)

    def call(self, method: str, *params: Any) -> Any:
        return self._post(method, self._params(list(params)))

    def _post(self, method: str, params: list) -> Any:
        payload = {"jsonrpc": "2.0", "id": str(next(_ids)), "method": method, "params": params}
        try:
            r = self.client.post(self.url, json=payload)
        except httpx.HTTPError as e:
            raise NasError(f"aria2 RPC unreachable at {self.url} ({e}). Is the aria2 container running? "
                           "On the NAS: `docker compose -f ~/nas-mcp/src/deploy/aria2/docker-compose.yml up -d`.") from None
        d = r.json()
        if "error" in d:
            raise NasError(f"aria2 {method} failed: {d['error'].get('message')}")
        return d["result"]

    def multicall(self, calls: list[tuple[str, list]], batch: int = 500) -> list:
        """Returns one entry per call: the result, or {'faultCode', 'faultString'} on error."""
        out: list = []
        for i in range(0, len(calls), batch):
            chunk = [{"methodName": m, "params": self._params(p)} for m, p in calls[i:i + batch]]
            res = self._post("system.multicall", [chunk])  # token goes inside each sub-call, not here
            out.extend(r[0] if isinstance(r, list) and r else r for r in res)
        return out

    def version(self) -> dict:
        return self.call("aria2.getVersion")

    def global_stat(self) -> dict:
        return self.call("aria2.getGlobalStat")
