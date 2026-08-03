"""Entry: python -m bluesky_mcp.

Dual transport (tauri_nsis_building.md):
- MCP_PORT or PORT set  -> HTTP daemon (uvicorn on 127.0.0.1)
- HTTP daemon reachable -> stdio proxy (SOTA_REQUIREMENTS.md §2.3)
- otherwise             -> stdio FastMCP (Claude Desktop / Cursor)
"""

import asyncio
import os

import httpx

from bluesky_mcp import outbox
from bluesky_mcp.server import main, mcp

HTTP_URL = os.getenv("SERVER_API_URL", "http://127.0.0.1:10760")
MCP_URL = f"{HTTP_URL}/mcp"


def _http_daemon_reachable() -> bool:
    try:
        r = httpx.post(
            MCP_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "bluesky-probe", "version": "1"},
                },
            },
            headers={"Accept": "application/json, text/event-stream"},
            timeout=3,
        )
        return r.status_code == 200
    except Exception:
        return False


if __name__ == "__main__":
    if os.environ.get("MCP_PORT") or os.environ.get("PORT"):
        main()
    elif _http_daemon_reachable():
        from fastmcp.server import create_proxy

        proxy = create_proxy(MCP_URL, name="bluesky-mcp")
        asyncio.run(proxy.run_stdio_async(show_banner=False))
    else:
        outbox._db()
        asyncio.run(mcp.run_stdio_async(show_banner=False))
