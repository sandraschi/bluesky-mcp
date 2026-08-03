# Product Requirements Document — bluesky-mcp

**Status:** Implemented · v0.1.1 (2026-08-03) · Public
**Ports:** 10760 backend (FastAPI + MCP `/mcp`) · 10761 webapp
**Transport:** dual — stdio (Claude Desktop/Cursor) · streamable HTTP (remote clients)
**Lane:** Comms — AT Proto / Bluesky (sibling: mastodon-mcp for ActivityPub)

---

## 1. Executive Summary

bluesky-mcp is the fleet's **Bluesky (AT Protocol) bridge with a human-approved outbox**.
Agents and `fleet-public-relations-mcp` enqueue promotion drafts; a human reviews and
approves; publish respects a dry-run default so nothing ever hits the public timeline
accidentally. It ships a SOTA dark webapp (Compose, Outbox, Inbox, Timelines, Chat,
Tools, Skills, Settings, Help) and a certified Tauri/NSIS desktop installer.

## 2. Product Overview

| Aspect | Description |
|--------|-------------|
| What it does | Reads/writes Bluesky (post, reply, boost, media, timelines, notifications), plus a SQLite outbox with human approval gates and inbound webhooks |
| Why it exists | Agents draft. Humans approve. No auto-posting, no hype, no AI-authorship theater (FLEET_PROMOTION.md) |
| Protocol | AT Proto (`com.atproto.*`, `app.bsky.*`) against a configurable PDS (default bsky.social) |
| Not | Mastodon/ActivityPub, a scheduler, a bot, or an auto-poster |

## 3. Users & Personas

| Persona | Uses |
|---------|------|
| **Sandra (fleet maintainer)** | Approve/publish release posts from the outbox; compose with AI assist; monitor notifications |
| **fleet-public-relations-mcp (agent)** | REST `POST /api/v1/outbox` — enqueue FLEET_PROMOTION drafts programmatically |
| **Cursor / Claude Desktop (agent)** | `bluesky_social_tool` portmanteau over MCP (stdio or HTTP) |
| **Any Bluesky user on the fleet** | Webapp for manual compose/review; optional custom PDS |

## 4. Goals

1. **Human-gated publishing** — nothing posts without an explicit approve (dry-run default; `BLUESKY_REQUIRE_OUTBOX_APPROVAL=1`).
2. **One portmanteau** — `bluesky_social_tool` with all ops implemented (no stubs): post, reply, boost, upload_media, timeline, notifications, accounts, outbox CRUD, webhooks, push subscription.
3. **SOTA webapp** — catch-them-all pages, skill-first chat, local LLM glom-on, dark theme, data-testids, e2e.
4. **Dual distribution** — `.mcpb` (Claude Desktop) + certified NSIS installer (embedded PyInstaller backend).
5. **Fleet lane fit** — REST handoff contract stable for `fleet-public-relations-mcp`; webhooks inbound with shared secret.

## 5. Non-Goals (v0.x)

- Auto-posting / scheduled campaigns / AI spam of any kind
- ActivityPub/Mastodon interop (that is mastodon-mcp) or cross-posting bridges
- Multi-account UI management (SQLite schema supports `accounts_list`; UI shows one profile)
- Media gallery management, DM/chat inbox, or moderation tooling (external labelers out of scope)
- Replacing bsky.app — the webapp is an MCP control surface, not a full Bluesky client

## 6. Functional Requirements

### 6.1 MCP tool surface (`bluesky_social_tool`)

| Operation | Behavior | Dry-run safe |
|-----------|----------|--------------|
| `post` | Create `app.bsky.feed.post`; **blocked** unless outbox-approved (or `REQUIRE_OUTBOX_APPROVAL=0`) | ✅ |
| `reply` | Reply to a post by `at://` URI (+ optional root/parent CIDs) | ✅ |
| `boost` / `repost` | Repost by status_id + cid | ✅ |
| `upload_media` | Upload blob → media id, reusable in posts | ✅ |
| `timeline` | home / local / public timelines | ✅ |
| `notifications` | Mentions, follows, boosts, replies | ✅ |
| `outbox_list/enqueue/approve/reject/publish` | Full outbox lifecycle; publish requires `approved` state | ✅ (publish) |
| `accounts_list` | Configured PDS/handle/DID/dry-run status | ✅ |
| `webhook_list/receive` | Inbound event queue with secret verification | ✅ |
| `push_subscription_get` | AT Proto push subscription state | ✅ |

Plus: `bluesky_help`, `bluesky_shutdown`, `show_outbox_card` (Prefab), `@mcp.resource("outbox://summary")`, `@mcp.prompt("bluesky_outbox_prompt")`, skills (`bluesky-outbox/SKILL.md`).

### 6.2 Outbox contract (the core)

- Enqueue: `POST /api/v1/outbox` — `{status_text, repo_id, campaign, visibility, source, idempotency_key, media_paths, cw_sensitive, spoiler_text, schema_version}`.
- List: `GET /api/v1/outbox?status=` — items with `pending/approved/published/rejected`.
- Approve / Reject / Publish: `POST /api/v1/outbox/{id}/{action}`.
- Publish = `bluesky_social(outbox_publish)` → requires `approved` → dry-run unless `BLUESKY_DRY_RUN=0`.
- Storage: SQLite (`data/outbox.sqlite3`; `%LOCALAPPDATA%\ai.fleet.bluesky-mcp` when frozen).

### 6.3 Webhooks

- `POST /api/v1/webhooks/inbound` — `X-Bluesky-Webhook-Secret` header vs `BLUESKY_WEBHOOK_SECRET`; stores event.
- `GET /api/v1/webhooks?limit=` — event list. (`webhook_receive` MCP op mirrors this.)

### 6.4 Webapp

Catch-them-all routes: Dashboard (hero + KPIs), Inbox (notifications), Outbox (approve/publish/reject), Compose (AI assist), Timelines, Tools, Skills, Chat (skill-first, 4 personalities, localStorage), Accounts, Settings (LLM providers + GPU + onboarding steps), Help page + Help/Logger modals. Real data only — no mock content; onboarding is a guided 4-step flow in Settings.

### 6.5 Safety model

| Guard | Default |
|-------|---------|
| `BLUESKY_DRY_RUN` | **1** — publish never posts |
| `BLUESKY_REQUIRE_OUTBOX_APPROVAL` | **1** — direct `post` blocked |
| Bind address | 127.0.0.1 only |
| Webhook secret | required for inbound |
| App password only | createSession never accepts the main password |

## 7. REST API (summary)

`/api/health` · `/api/status` · `/api/v1/diagnostics` · `/api/dashboard` · `/api/capabilities` · `/api/tools` · `/api/skills` · `/api/logs` (ring buffer) · `/api/llm/providers` (incl. GPU) · `/api/llm/chat` · `/api/compose/assist` · `/api/v1/outbox*` · `/api/v1/notifications` · `/api/v1/timeline` · `/api/v1/webhooks*`. Full reference: `docs/TOOLS.md`.

## 8. Architecture

```
MCP clients (stdio/HTTP)
   │
bluesky_mcp.server (FastAPI + FastMCP)
   ├── portmanteau.py  → client.py (AT Proto over httpx) → PDS (bsky.social)
   ├── outbox.py       → SQLite outbox (approve gates)
   ├── webhooks.py     → inbound event queue (secret)
   └── skills/         → SKILL.md provider
webapp (React/Vite/Tailwind/Zustand) → /api/* (Vite proxy dev; absolute API_BASE prod)
Tauri (NSIS) → embedded PyInstaller backend on 127.0.0.1:10760
```

Dual transport in `__main__.py`: `PORT`/`MCP_PORT` set → HTTP daemon; HTTP daemon reachable → stdio proxy (SOTA §2.3); else stdio.

## 9. Data & Persistence

- Outbox + webhook events: SQLite (single file; WAL). Schema versioned (`schema_version` on enqueue).
- No user data leaves the machine except the explicit AT Proto calls to the configured PDS.
- Frozen builds persist under `%LOCALAPPDATA%\ai.fleet.bluesky-mcp\` (never `_MEIPASS`).

## 10. Security Considerations

- App passwords only; secrets live in `.env` (gitignored), never bundled (`.env.example` only in installer).
- CORS: explicit origins + unconditional `allow_origin_regex` (Tauri, Tailscale, LAN) — no `["*"]`.
- Webhook secret verification; localhost bind; no shell execution; fixed-argv subprocess only for nvidia-smi GPU probe.
- No hardcoded secrets in source (ruff/grep gate).

## 11. Testing Strategy

- **Unit/integration** (24 tests): outbox lifecycle, portmanteau ops, client dry-run + credential gates, API e2e via TestClient. Coverage gate ≥ 60% (`pytest-cov`).
- **Playwright e2e** (4): backend health, inbound→approve→dry-publish, notifications, page walk.
- **CUA-NSIS** (11 phases): install → launch → backend health → diagnostics → uninstall (certified 2026-08-03).
- Gates: `just ci` = ruff + pyright + pytest + tsc + biome; pre-commit hooks materialized.

## 12. Success Metrics

- First release post goes out via outbox with zero direct-post bypasses.
- `fleet-public-relations-mcp` handoff stable (contract frozen at `schema_version 1`).
- Installer certified (CUA 11/11) and reproducible via `just build-native`.
- Zero CRITICAL/HIGH in assfix assessment (score 95/100, 2026-08-03).

## 13. Roadmap

| Item | Priority | Notes |
|------|----------|-------|
| Live-account verification pass | High | Mocked-HTTP tests for `client.py` AT Proto requests; optional throwaway-account smoke |
| Timelines feed rendering | Medium | Real post cards instead of raw JSON dump |
| Inbox actions | Medium | Reply/repost from notification rows |
| Multi-account UI | Low | Schema-ready (`accounts_list`); UI surfaces one profile |
| Compose media/reply UI | Low | Wire existing `upload_media`/`reply` ops into Compose |

## 14. Risks

| Risk | Mitigation |
|------|-----------|
| Live AT Proto calls unverified (no mocked-HTTP tests) | Roadmap item 1 before first real post |
| Rate limits / 429s from PDS | Client-side backoff; dry-run absorbs load in tests |
| Token leak | App-password-only, `.env` gitignored, rotate on leak |
| Protocol drift (AT Proto lexicon changes) | Pin SDK semantics via mocked tests; versioned schema |

---

See also: [docs/TOOLS.md](docs/TOOLS.md) (tool/REST reference) · [docs/CONFIGURATION.md](docs/CONFIGURATION.md) (env) · [docs/FEDIVERSE.md](docs/FEDIVERSE.md) (AT Proto vs fediverse) · [docs/ONBOARDING.md](docs/ONBOARDING.md) (account flow) · [BUILD_LOG.md](BUILD_LOG.md) (NSIS build history).
