"""Small HTTP helper with retries. Connectors take an Http instance so tests can fake it."""
from __future__ import annotations

import time
from typing import Any

import httpx

from . import NasError, __version__

UA = f"nas-mcp/{__version__} (+omics dataset fetcher)"


class Http:
    def __init__(self, timeout: float = 60.0, retries: int = 3):
        self.client = httpx.Client(timeout=timeout, follow_redirects=True, headers={"User-Agent": UA})
        self.retries = retries

    def request(self, method: str, url: str, **kw: Any) -> httpx.Response:
        last: Exception | None = None
        for attempt in range(self.retries):
            try:
                r = self.client.request(method, url, **kw)
                if r.status_code in (429, 500, 502, 503, 504) and attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                if r.status_code >= 400:
                    raise NasError(f"{method} {url.split('?')[0]} -> HTTP {r.status_code}: {r.text[:300]}")
                return r
            except httpx.HTTPError as e:
                last = e
                time.sleep(2 ** attempt)
        raise NasError(f"{method} {url.split('?')[0]} failed after {self.retries} tries: {last}")

    def get_json(self, url: str, params: dict | None = None, headers: dict | None = None) -> Any:
        return self.request("GET", url, params=params, headers=headers).json()

    def post_json(self, url: str, payload: dict, headers: dict | None = None) -> Any:
        return self.request("POST", url, json=payload, headers=headers).json()

    def get_text(self, url: str, params: dict | None = None, headers: dict | None = None) -> str:
        return self.request("GET", url, params=params, headers=headers).text

    def get_json_paged(self, url: str, params: dict | None = None, headers: dict | None = None,
                       max_pages: int = 1000) -> list:
        """Follow RFC 5988 `Link: <...>; rel="next"` pagination, concatenating JSON lists."""
        out: list = []
        next_url: str | None = url
        for _ in range(max_pages):
            if not next_url:
                break
            r = self.request("GET", next_url, params=params, headers=headers)
            out.extend(r.json())
            params = None
            next_url = r.links.get("next", {}).get("url")
        return out
