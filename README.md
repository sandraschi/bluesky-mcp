# bluesky-mcp

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.4%2B-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <a href="https://github.com/sandraschi/bluesky-mcp/actions"><img src="https://img.shields.io/github/actions/workflow/status/sandraschi/bluesky-mcp/ci.yml?branch=master&style=flat-square" alt="CI"></a>
  <a href="https://atproto.com/"><img src="https://img.shields.io/badge/AT%20Proto-Bluesky-0085FF?style=flat-square" alt="AT Proto"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="MIT"></a>
</p>

**Bluesky / AT Proto** client — compose, timelines, and a **human-approved outbox** for promotion drafts from `fleet-public-relations-mcp`.

**v0.1.1** · Ports **10760** / **10761** · Sibling of [discord-mcp](https://github.com/sandraschi/discord-mcp) · ActivityPub sibling [mastodon-mcp](https://github.com/sandraschi/mastodon-mcp)

> FastMCP 3.4+ · full portmanteau (reply/repost/media/webhooks) · SOTA webapp · dry-run default · Windows CI + local `just ci`

> Bluesky = AT Proto. **Not** Mastodon / ActivityPub.

---

## Principle

Agents draft. Humans approve. Nothing posts without outbox approve → publish.

Tone: [`FLEET_PROMOTION.md`](../mcp-central-docs/standards/FLEET_PROMOTION.md).

---

## Features

- Human-approved outbox + fleet-PR REST handoff
- Full `bluesky_social` ops: post, reply, Repost, media, timelines, notifications, webhooks
- Dark SOTA webapp: Dashboard, Inbox, Outbox, Compose (AI assist), Chat, Skills, Tools, Settings, Help
- Dry-run default; inbound webhooks with shared secret
- Ruff + Biome + pytest gate; Windows-only CI workflow

---

## Quick start

```powershell
cd D:\Dev\repos\bluesky-mcp
Copy-Item .env.example .env
# Edit BLUESKY_INSTANCE + BLUESKY_ACCESS_TOKEN
.\start.bat
```

Dashboard: http://127.0.0.1:10761 · MCP: http://127.0.0.1:10760/mcp

---

## Documentation

| Doc | Contents |
|-----|----------|
| [INSTALL.md](INSTALL.md) | Install paths |
| [docs/ONBOARDING.md](docs/ONBOARDING.md) | First-timer: account, money/CC, pitfalls, sanity check |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Env vars |
| [docs/TOOLS.md](docs/TOOLS.md) | MCP + REST reference |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Lint, `just ci`, packaging |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Symptom → fix |

---

## Ports

| Service | Port |
|---------|------|
| Backend | **10760** |
| Webapp | **10761** |

---

## MCP tools

Portmanteau **`bluesky_social`** — all operations implemented (see [docs/TOOLS.md](docs/TOOLS.md)). Also `bluesky_help`, `bluesky_shutdown`, `show_outbox_card`.

---

## Quality

```powershell
just ci
```

Private repos: GitHub Actions stay disabled at account level (billing). Workflow file is still required; run `just ci` locally.

---

## License

MIT (see LICENSE if present)
