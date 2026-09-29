"""Speak real MCP over stdio to the server subprocess, the same way Claude Code does via SSH."""
import json
import os
import sys

import anyio
import pytest

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def _is_error(result) -> bool:
    return bool(getattr(result, "is_error", None) or getattr(result, "isError", None))


def _text(result) -> str:
    return "".join(getattr(c, "text", "") for c in result.content)


def test_stdio_protocol(cfg):
    params = StdioServerParameters(command=sys.executable, args=["-m", "nas_mcp.server"],
                                   env={**os.environ, "NAS_MCP_CONFIG": str(cfg.source_path)})

    async def go():
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                names = {t.name for t in (await s.list_tools()).tools}
                assert {"nas_plan_dataset", "nas_submit_plan", "nas_job_status", "nas_verify_job"} <= names
                assert len(names) == 14

                hits = json.loads(_text(await s.call_tool("nas_catalog_search", {"query": "olink"})))
                assert {"ukb-ppp-individual", "ukb-ppp-pqtl"} <= {h["id"] for h in hits}

                refused = await s.call_tool("nas_plan_dataset", {"dataset_id": "gnpc"})
                assert _is_error(refused) and "Nothing was queued" in _text(refused)

                bad = await s.call_tool("nas_create_folder", {"path": "../../etc/x"})
                assert _is_error(bad) and "outside the allowed roots" in _text(bad)

                ok = json.loads(_text(await s.call_tool("nas_create_folder", {"path": "singlecell/sea-ad"})))
                assert ok["created"] is True
                listed = json.loads(_text(await s.call_tool("nas_list_folders", {"depth": 2})))
                assert "singlecell/sea-ad/" in listed["folders"]
                assert json.loads(_text(await s.call_tool("nas_storage_overview", {})))

    anyio.run(go)
