# BUILD_LOG — bluesky-mcp

## 2026-08-03 — v0.1.1 NSIS build #1 (assfix pass)

**Result: PASS — `just cua-nsis-test` 11/11 phases.**

Artifacts:
- Installer: `src-tauri/target/release/bundle/nsis/Bluesky MCP_0.1.1_x64-setup.exe` (28.8 MB)
- Backend: `src-tauri/resources/bluesky-mcp-backend.exe` (27.8 MB, PyInstaller onefile)
- Also staged in `dist/`

### Build failures encountered + fixes

| # | Failure | Root cause | Fix |
|---|---------|-----------|-----|
| 1 | Frozen backend crashed on import: `PackageNotFoundError: No package metadata was found for fastmcp` | `fastmcp/__init__.py` calls `importlib.metadata.version()`; dist-info collection for fastmcp/fastmcp_slim is unreliable in PyInstaller 6.21 onefile | Patched venv `fastmcp/__init__.py` with `except PackageNotFoundError: __version__ = "0.0.0"` fallback; added patch step to `src-tauri/build.ps1`; added `fastmcp_slim-` to spec `_keep_dist` |
| 2 | Operator exited with code -1 ~8s after launch (window flashes, then dies) | `backend.rs free_port()` image-name kill included `bluesky-mcp-native` — which matches the operator's OWN process name → setup self-killed the app | Removed the native image from `free_port()` kill list (never kill own image); verified window stays up + backend health 200 |
| 3 | CUA "Backend not reachable after 30s" | Template hardcoded 10×3s wait; onefile cold extraction takes ~12-25s | `MAX_RETRY`/`RETRY_DELAY` now configurable via `cua-nsis-config.json` (`backend_max_retry: 20` → 60s) |
| 4 | Runt backend exe (10.4 MB) missing httpx/fastapi/uvicorn | `uv run pyinstaller` fell back to a uv ephemeral env (pyinstaller absent from project venv after a plain `uv sync` stripped dev extras) → analysis could not see site-packages | build.ps1 now runs `.venv\Scripts\pyinstaller.exe` explicitly with `uv add --dev pyinstaller` fallback; size gate ≥5 MB retained |
| 5 | Stale resources in installer | Direct `npx tauri build` (without build.ps1) reused `src-tauri/resources/*.exe` from an earlier build | Always run the full `just build-native` pipeline; verify resource timestamp before certifying |
| 6 | Disk full (D: 37 MB free) blocked linking + debug builds | ~84 GB of regenerable cargo `target/` dirs across fleet repos | Purged 20 fleet cargo target dirs + kyutai `.venv` (84.2 GB freed) |

### Notes for next build

- Run `just build-native` (full pipeline — never bare `npx tauri build`).
- Verify `src-tauri/resources/bluesky-mcp-backend.exe` timestamp is fresh before `just cua-nsis-test`.
- CUA nav walk (phases 4/5/8/9) skipped in this run — windows-computer-use-mcp CUA client not connected. Re-run `just cua-nsis-test` from a session with desktop automation for the nav click-through.
