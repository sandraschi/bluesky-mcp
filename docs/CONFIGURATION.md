# Configuration — bluesky-mcp

Copy `.env.example` to `.env` and edit.

| Variable | Default | Purpose |
|----------|---------|---------|
| `BLUESKY_INSTANCE` | — | Base URL, e.g. `https://bsky.social` |
| `BLUESKY_ACCESS_TOKEN` | — | App token (`read`, `write:statuses`, `write:media`, `push` optional) |
| `BLUESKY_DRY_RUN` | `1` | `1` = simulate writes; `0` = live |
| `BLUESKY_REQUIRE_OUTBOX_APPROVAL` | `1` | Block direct `post` without outbox |
| `BLUESKY_BACKEND_PORT` | `10760` | FastAPI + MCP |
| `BLUESKY_DATA_DIR` | `%LOCALAPPDATA%\bluesky-mcp` | SQLite outbox + webhooks |
| `BLUESKY_WEBHOOK_SECRET` | — | Shared secret for `POST /api/v1/webhooks/inbound` |
| `BLUESKY_LOG_LEVEL` | `INFO` | Logging |
| `PORT` | (backend port) | Override bind port (Tauri / packagers) |

Frontend Vite port is **10761** (fixed in `webapp/vite.config.ts` / `start.ps1`).

Claude Desktop / Cursor `env` block should pass the same keys when using stdio or HTTP MCP.
