# Changelog

## v0.1.2 (2026-08-03) — assfix pass

- **Dual transport**: `python -m bluesky_mcp` now falls back to stdio (Claude Desktop/Cursor) when no `PORT`/`MCP_PORT` env; proxies to a running HTTP daemon when present (SOTA §2.3)
- **CORS**: unconditional `allow_origin_regex` (Tailscale, LAN, tauri origins)
- REST: added `GET /api/status`, `GET /api/v1/diagnostics` (CUA-NSIS), live `/api/logs` ring buffer
- Tool surface: `annotations=` + `output_schema=` on MCP tools; `@mcp.resource("outbox://summary")`; `err_response()` helper with auto-logging
- Webapp: `API_BASE` lib (absolute backend URLs — fixes Tauri "Failed to fetch" class), Tauri `backend-status` listener + Restart Backend button, exponential backoff health poll, `useZoom()` Ctrl+Scroll zoom, provider/model select persistence (`llm_provider`/`llm_model`), 6 example prompts, data-testids on all pages, contrast pass (zinc-500/600 → 400, text-xs bumps)
- Native: generated icons, PyInstaller spec per fleet template (`noarchive=True`, `upx=False`), fixed `MASTODON_*` env copy-paste bug → `BLUESKY_*`, multi-layer `free_port()`, stream watching + `start_backend` invoke command
- Plumbing: `.pre-commit-config.yaml` + `scripts/pre-commit-biome.ps1`, session context injection (`.claude-plugin`, `.cursorrules`, `.windsurfrules`, copilot-instructions, `.opencode` skill), CUA scripts + `just cua-webapp-test`/`cua-nsis-test`, `just fmt`/`bootstrap`/`certify`, pyright + pytest-cov in dev deps (five-gate), `renovate.json`, coverage gate ≥60%, glama/manifest version 0.1.1
- Fixes: e2e strict-mode selector (persisted outbox duplicates), `.gitignore` dedupe, removed bak dross

## v0.1.1 (2026-07-26)

- SOTA webapp catch-them-all: Dashboard (hero + KPIs), Inbox, Tools, Skills, Chat, Help page, Logs modal
- Settings: LLM provider/model probe (Ollama / LM Studio / vLLM)
- Compose: AI assist via `POST /api/compose/assist`
- REST: `/api/dashboard`, `/api/skills`, `/api/tools`, `/api/llm/*`, `/api/logs`
- **Full tools** (no planned stubs): `reply`, `boost`, `upload_media`, webhook inbound + list, push subscription get
- docs/: CONFIGURATION, DEVELOPMENT, TOOLS, TROUBLESHOOTING
- Windows-only CI workflow + `just ci` (ruff + biome + pytest + tsc)
- `BLUESKY_WEBHOOK_SECRET` + `POST /api/v1/webhooks/inbound`

## v0.1.0 (2026-07-26)

- Initial FastMCP 3.4+ Bluesky bridge with human-approved outbox
- REST handoff for fleet-public-relations-mcp (`POST /api/v1/outbox`)
- Dark webapp: Outbox, Compose, Timelines, Accounts, Settings
- Dry-run default; notifications inbox dry stub
- Tests: pytest API/outbox/portmanteau + Playwright e2e
- MCPB pack, Tauri/NSIS scaffold, FleetStartMode launcher
- Ports 10760/10761 registered in WEBAPP_PORTS.md
- Private (`.nopublish`) — no GitHub Actions
