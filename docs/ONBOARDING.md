# Onboarding — bluesky-mcp

## What this is for

**bluesky-mcp** is an AT Proto bridge for the sandraschi fleet. Agents and `fleet-public-relations-mcp` enqueue promotion drafts into a **human-approved outbox**. You review, approve, then publish to Bluesky.

It is **not** an auto-poster and **not** Mastodon/ActivityPub. Default mode is dry-run so nothing hits the public timeline until you say so. The outbox (drafts, approve, dry-run publish) works with **zero credentials** — only live posting needs an account.

## Cost and accounts (money / CC)

| Question | Answer |
|----------|--------|
| Do I need an account? | **Yes** for live posting — a Bluesky account (bsky.social or a compatible PDS) |
| Free tier? | **Yes** on bsky.social for typical personal use |
| Credit card required? | **No** for a normal Bluesky account |
| Ongoing cost? | Free for typical use; optional custom PDS hosting is separate |
| Who bills? | Bluesky / your PDS host (if anyone) — not sandraschi / not this MCP |

## Step 1 — Get Bluesky (download / install / account)

Bluesky is free and open (AT Protocol). Pick any one path — they all share the same account:

| Path | Where | Notes |
|------|-------|-------|
| **Web** | [bsky.app](https://bsky.app) | Fastest — no install |
| **iOS / iPadOS** | App Store → “Bluesky Social” | Same account as web |
| **Android** | Google Play → “Bluesky Social” | Same account as web |
| **Desktop** | [bsky.app](https://bsky.app) works in any browser; there is no official native Windows/macOS client — the web app is the desktop client | The MCP webapp dashboard is at `http://127.0.0.1:10761` and does not need the Bluesky app at all |
| **Custom PDS** (advanced) | Self-hosted or third-party PDS | Same protocol; set `BLUESKY_PDS` to your instance URL |

1. Sign up at [bsky.app](https://bsky.app) — email + a handle (default `<you>.bsky.social`, or a custom domain later).
2. If you plan to post from the phone apps later, install one and log in — otherwise the web account is enough.
3. (Optional but recommended) set your profile: display name, avatar, and a starter “about” line. The fleet drafts will look better with a real profile behind them.

## Step 2 — Create an app password

Bluesky requires a per-app password for third-party tools — **never** your login password.

1. Log in at [bsky.app](https://bsky.app).
2. Go to **Settings → Privacy and security → App Passwords** (direct: https://bsky.app/settings/app-passwords).
3. **Add app password**, name it e.g. `bluesky-mcp`.
4. Copy the generated `xxxx-xxxx-xxxx-xxxx` string **once** — it is shown a single time.

## Step 3 — Configure the server

```powershell
cd D:\Dev\repos\bluesky-mcp
Copy-Item .env.example .env
```

Edit `.env`:

```ini
BLUESKY_PDS=https://bsky.social        # or your custom PDS
BLUESKY_HANDLE=you.bsky.social          # your handle, no @
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # app password from step 2
BLUESKY_DRY_RUN=1                        # keep 1 until you mean it
```

Start:

```powershell
.\start.bat
```

Dashboard: **http://127.0.0.1:10761** · Backend: **http://127.0.0.1:10760**

## Step 4 — Verify

| Check | Expected |
|-------|----------|
| `GET http://127.0.0.1:10760/api/health` | `"instance_configured": true` |
| Settings page | Green “Backend” row + onboarding card disappears |
| **Inbox** | Real Bluesky notifications (mentions / follows / boosts) appear |
| **Timelines** | Fetch returns real home / local / public timelines |
| Compose → Enqueue → Outbox → Approve → Publish | `"dry_run": true` — nothing posted yet |

## Step 5 — Go live (when ready)

1. Set `BLUESKY_DRY_RUN=0` in `.env`.
2. Restart the backend.
3. Dashboard badge flips from **DRY RUN** to **LIVE POSTING**.
4. First live post: Compose a real draft → Outbox → Approve → Publish → verify it appears at your profile on [bsky.app](https://bsky.app).

To go back to safety, set `BLUESKY_DRY_RUN=1` and restart.

## Pitfalls

- **Dry-run default** — publish “succeeds” but does not post. Flip `BLUESKY_DRY_RUN=0` only when you mean it, then restart.
- **Direct `post` blocked** — fleet path is outbox → approve → publish (`BLUESKY_REQUIRE_OUTBOX_APPROVAL=1`).
- **Main password vs app password** — `createSession` expects an **app password**, not your account password.
- **Secrets in git** — never commit `.env`. Rotate the app password if it leaks (App Passwords → revoke).
- **Tone** — fleet drafts follow `FLEET_PROMOTION.md` (no hype, no “written by AI” theater).
- **Not Mastodon** — Bluesky is AT Proto, not ActivityPub. Do not paste Mastodon tokens into Bluesky fields. See [FEDIVERSE.md](FEDIVERSE.md) for how both fit together.
- **Wrong account** — if health says not configured after setup, check the handle has no `@` and the app password has no spaces.

## What works before onboarding (honest list)

With no credentials the server still runs fully for the local workflow:

- Outbox: enqueue / list / approve / reject / **dry-run** publish (SQLite, no network)
- Compose, Dashboard KPIs, Tools/Skills discovery, Chat (needs a local LLM), Settings, Help
- Webhooks inbound/outbound

Only live AT Proto calls (post, reply, boost, upload_media, timeline, notifications) require the account in Step 1–3.
