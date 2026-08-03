# Changelog

## v0.1.3 (2026-08-03) — real data + docs pass

- **Mocks removed** — Dashboard/Outbox/Inbox always show real data (empty states instead of fake sample content); deleted `mockOnboarding.ts` + `MockBadge.tsx`; onboarding CTAs link to the guided flow
- **Onboarding upgraded** — Settings now shows a 4-step guide (create account → app password → `.env` → restart) with direct links (bsky.app, App Passwords); `docs/ONBOARDING.md` rewritten with download/install/account flow for web/iOS/Android/custom PDS
- **New `docs/FEDIVERSE.md`** — Bluesky/AT Proto vs ActivityPub fediverse explained: federation models, handles/DID, relay vs instance federation, fleet comms lane map (bluesky/mastodon/discord/email), cross-posting reality, glossary
- **PRD.md rewritten** — executive summary, personas, goals/non-goals, functional requirements, outbox contract, safety model, architecture, data/security, testing, success metrics, roadmap (live-verification pass first), risks
- **MCD project page** — `mcp-central-docs/projects/bluesky-mcp/README.md` created; row added to `FLEET_INDEX.md`
- README/llms.txt link the new docs

## v0.1.2 (2026-08-03) — assfix pass

### Round 2 (fix all): NSIS build + certification

- **CI fix**: dev deps consolidated into `[dependency-groups] dev` (uv `add --dev` had split pre-commit into a second group → fleet-ci synced only pre-commit → ruff missing). All tools (ruff/pyright/pytest/pyinstaller/pre-commit) now install via plain `uv sync`

- **First certified NSIS build**: `Bluesky MCP_0.1.1_x64-setup.exe` (28.8 MB), `just cua-nsis-test` 11/11 phases PASS (install → backend health → feature route → diagnostics → uninstall). See `BUILD_LOG.md`
- **Fixed operator self-kill**: `backend.rs free_port()` killed the operator's own image (`bluesky-mcp-native` matched its own process name → app exited -1 ~8s after launch)
- **Fixed runt PyInstaller exe**: `uv run pyinstaller` fell back to a uv ephemeral env (missing site-packages → 10.4 MB exe without httpx/fastapi). build.ps1 now runs `.venv\Scripts\pyinstaller.exe` explicitly with install fallback
- **Frozen persistence**: `data/` now resolves to `%LOCALAPPDATA%\ai.fleet.bluesky-mcp` when frozen (was `_MEIPASS` temp dir)
- **Spec hardening**: joserfc/h11/beartype/websockets/sqlite3/_strptime/_datetime hiddenimports, eager `_strptime`/`_datetime` imports, `fastmcp_slim-` dist-info keep
- **GPU opportunity prompt**: `GET /api/llm/providers` now returns `gpu` (nvidia-smi); Settings shows "install Ollama/LM Studio" CTA when GPU detected but no provider running (`data-testid="gpu-opportunity"`)
- **CUA script**: backend wait now configurable (`backend_max_retry`/`backend_retry_delay`) — onefile cold start needs >30s
- **pre-commit**: hooks materialized (`.git/hooks/pre-commit`), `pre-commit` added to dev deps
- **BUILD_LOG.md** created with 6 build failures + fixes documented

### Round 1 (assess): SOTA plumbing

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
