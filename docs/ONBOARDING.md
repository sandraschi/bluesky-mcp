# Onboarding — bluesky-mcp

## What this is for

**bluesky-mcp** is an AT Proto bridge for the sandraschi fleet. Agents and `fleet-public-relations-mcp` enqueue promotion drafts into a **human-approved outbox**. You review, approve, then publish to Bluesky.

It is **not** an auto-poster and **not** Mastodon/ActivityPub. Default mode is dry-run so nothing hits the public timeline until you say so.

## Cost and accounts (money / CC)

| Question | Answer |
|----------|--------|
| Do I need an account? | **Yes** — a Bluesky account (bsky.app or compatible PDS) |
| Free tier? | **Yes** on bsky.social for typical personal use |
| Credit card required? | **No** for a normal Bluesky account |
| Ongoing cost? | Free for typical use; optional custom PDS hosting is separate |
| Who bills? | Bluesky / your PDS host (if anyone) — not sandraschi / not this MCP |

## Prerequisites outside this repo

- A Bluesky **handle** you control (e.g. `you.bsky.social`)
- An **app password** from bsky.app → Settings → App Passwords (not your main login password)
- Optional: `BLUESKY_WEBHOOK_SECRET` if other fleet tools POST to `/api/v1/webhooks/inbound`

Install tooling (uv, Node, git) is covered in [INSTALL.md](../INSTALL.md).

## First-timer setup steps

1. Create or log into Bluesky in a browser.
2. Open **Settings → Privacy and security → App Passwords** (wording may vary slightly).
3. Create an app password named e.g. `bluesky-mcp`, copy it once.
4. In the repo:
   ```powershell
   cd D:\Dev\repos\bluesky-mcp
   Copy-Item .env.example .env
   ```
5. Edit `.env`:
   - `BLUESKY_PDS=https://bsky.social` (or your custom PDS)
   - `BLUESKY_HANDLE=you.bsky.social`
   - `BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx`
   - Keep `BLUESKY_DRY_RUN=1` until you intentionally go live
6. Start: `.\start.bat` → dashboard http://127.0.0.1:10761
7. Open **Settings** — confirm health shows configured (`instance_configured: true`).
8. Enqueue a test draft on **Compose** or **Outbox**, approve, publish — expect `dry_run: true` until you set `BLUESKY_DRY_RUN=0`.

## Pitfalls

- **Dry-run default** — publish “succeeds” but does not post. Flip `BLUESKY_DRY_RUN=0` only when you mean it, then restart the backend.
- **Direct `post` blocked** — fleet path is outbox → approve → publish (`BLUESKY_REQUIRE_OUTBOX_APPROVAL=1`).
- **Main password vs app password** — createSession expects an **app password**, not your account password.
- **Secrets in git** — never commit `.env`. Rotate the app password if it leaks.
- **Tone** — fleet drafts follow `FLEET_PROMOTION.md` (no hype, no “written by AI” theater).
- **Not Mastodon** — different protocol; do not paste Mastodon tokens into Bluesky fields.

## Sanity check

| Check | Expected |
|-------|----------|
| `GET http://127.0.0.1:10760/api/health` | `"instance_configured": true` when handle + app password set |
| Settings page | Shows account configured; LLM probe is separate (optional) |
| Outbox publish with dry_run | `"success": true`, `"dry_run": true`, message about not posted |
| Inbox without credentials | Empty list + dry message — UI may show MOCK samples until onboarded |

## Declared doubles

See [DEVELOPMENT.md](DEVELOPMENT.md) § Declared doubles. Without finishing this onboarding, the server still runs: dry-run writes, empty notifications API, local outbox SQLite.

### Mock-until-onboarded (webapp)

Until `instance_configured` is true, the dashboard shows a **big red** “Complete onboarding” button under the hero, plus **MOCK**-badged sample KPIs / outbox rows and inbox messages from **Joe Mocky** and **Sandra Mockinger**. Those UI samples are declared in `webapp/src/lib/mockOnboarding.ts` and disappear automatically after you set handle + app password — they are not live AT Proto data.
