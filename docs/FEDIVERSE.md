# Bluesky, AT Proto, and the Fediverse — where this server sits

**bluesky-mcp** speaks one protocol: **AT Protocol (AT Proto)** — the network behind Bluesky.
It is **not** an ActivityPub server, and "the fediverse" is a bigger, older, and different
network. This doc explains the landscape so you never confuse the two, and shows where
this MCP server sits in the sandraschi fleet's comms layer.

---

## 1. The two networks in one picture

```
                   FEDIVERSE                          BLUESKY / AT PROTO
   (ActivityPub — Mastodon, Pixelfed,           (AT Proto — Bluesky + other PDSs)
    PeerTube, Lemmy, Misskey, ~10-15k instances)

   mastodon.social  ──┐                     bsky.social (PDS)  ──┐
   fosstodon.org   ──┤   instance-to-instance                 ├── relay (Big Sky,
   chaos.social    ──┴   federation (push/pull                │   bsky.network)
                        ActivityPub objects)                  │   index + feed fan-out
                                                              └   PDS-to-relay
   Handle: @you@mastodon.social              Handle: you.bsky.social
   Identity: instance-bound                  Identity: DID (portable)
```

Both are **open, decentralized social networks** — that is where the similarity ends.

| | **Fediverse (ActivityPub)** | **Bluesky (AT Proto)** |
|---|---|---|
| Started | 2016 (Mastodon 2016, protocol older) | 2019 (Twitter/X alumni) |
| Protocol | ActivityPub (W3C standard) | AT Protocol (open spec, bsky team) |
| **Federation model** | **Instance federation**: each server (Mastodon instance) peers directly with others; you follow the server, your identity lives on it | **PDS + relay**: users host on a Personal Data Server; a Relay (Big Sky) indexes the firehose and fans feeds out; servers don't peer pairwise |
| Handle | `@user@instance.domain` — changes if you migrate | `user.bsky.social` — or your own domain; backed by a portable **DID** (`did:plc:...` / `did:web:...`) |
| Moderation | Per-instance (blocklists, defederation) | Layered: PDS + relay + independent labelers + moderation services |
| Data model | ActivityPub objects/activities (Note, Follow, Like...) | AT Proto records + Lexicons (app.bsky.feed.post, ...) |
| Following | Follower graph per instance | Follows as data records (exportable), firehose = public stream |
| Interop with the other | **None** — protocols don't speak | **None** — protocols don't speak |
| Clients | Mastodon web/APIs, MastoAPI-compatible apps | Bluesky app, AT Proto SDKs, MCP servers like this one |

**The one-liner:** the fediverse is a network of cooperating servers that exchange
ActivityPub; Bluesky is a network of personal data servers feeding a shared relay —
same category (open social web), different protocol, zero interoperability.

## 2. AT Proto concepts you'll see in this repo

| Term | Meaning |
|------|---------|
| **PDS** | Personal Data Server — where your account's data lives (bsky.social is the big one; you can host your own) |
| **DID** | Decentralized Identifier — the stable account id (`did:plc:...`), independent of handle |
| **Handle** | Human name (`you.bsky.social`, or a custom domain verified via DNS) |
| **Relay** | Ingests every public post (the "firehose") and distributes to app views — Big Sky, bsky.network |
| **App View** | Serves filtered feed data to clients (e.g. bsky.app, this MCP) |
| **Lexicon** | The typed schema for records (`app.bsky.feed.post` = a post record) |
| **Record** | An individual piece of data (post, follow, like) stored on a PDS |
| **AT URI** | `at://did:plc:xxx/app.bsky.feed.post/yyy` — stable reference to a record |
| **Skeet** | Community slang for a Bluesky post |

**In this repo:** `client.py` talks to the PDS via AT Proto (com.atproto.* and
app.bsky.* endpoints). `BLUESKY_PDS` points at the PDS (`https://bsky.social` default),
`BLUESKY_HANDLE` + `BLUESKY_APP_PASSWORD` authenticate via `com.atproto.server.createSession`.
Posts are `app.bsky.feed.post` records; media uploads are `com.atproto.repo.uploadBlob`.

## 3. Why Bluesky exists alongside Mastodon

The fleet runs **both** `bluesky-mcp` (AT Proto) and `mastodon-mcp` (ActivityPub) because
they reach different audiences:

- **Mastodon / ActivityPub** → the open-source, instance-federation world; tech +
  academic communities, EU institutions (e.g. EUvoice), self-hosters.
- **Bluesky / AT Proto** → the post-Twitter mainstream-adjacent crowd; creators,
  journalists, media, and the fast-growing AT Proto dev ecosystem.
- **Discord** (`discord-mcp`) and **email** (`email-mcp`) fill the closed-network lanes.

Promotion drafts for fleet MCP repos are written **once** in the human-approved outbox
and can be queued to whichever lane (or lanes) the release calls for. Each lane keeps its
own protocol, its own tone rules, and its own outbox row.

## 4. Fleet comms lane map

| Lane | Repo | Protocol / surface | Outbox |
|------|------|--------------------|--------|
| Bluesky | **bluesky-mcp** | AT Proto (PDS + relay) | Yes — human approve → dry-run → live |
| Mastodon | mastodon-mcp | ActivityPub (Mastodon API) | Yes — same pattern |
| Discord | discord-mcp | Discord bot API (guilds, channels) | n/a (immediate send) |
| Email | email-mcp | IMAP/SMTP | Draft → send flow |

`fleet-public-relations-mcp` is the drafting side: it produces FLEET_PROMOTION-compliant
copy and enqueues it to the outbox lane(s). bluesky-mcp is deliberately the **safest**
lane: dry-run default + outbox approval gate, so a bad prompt can never hit the public
timeline by accident.

## 5. Cross-posting reality check

There is **no built-in bridge** between Bluesky and the fediverse:

- Fediverse users can sometimes follow Bluesky handles through third-party bridge
  services, and vice versa — but those are unofficial, rate-limited, and not part of
  either protocol.
- If a release should appear on both networks, queue it to **both outboxes** (bluesky-mcp
  + mastodon-mcp) and approve each side — that is the fleet pattern.

## 6. Glossary quick scan

- **Fediverse** — the loose network of ActivityPub servers (Mastodon, Pixelfed, PeerTube, Lemmy...)
- **ActivityPub** — W3C standard protocol those servers speak
- **Mastodon** — the most popular ActivityPub software (microblogging)
- **Bluesky** — the app + company behind the AT Protocol network
- **AT Protocol / atproto** — the open protocol Bluesky is built on
- **PDS / Relay / App View** — the three tiers of AT Proto infrastructure
- **DID** — portable identity; **handle** — human-readable name pointing at a DID

## 7. Further reading

- [AT Protocol spec](https://atproto.com/) — lexicons, DID, PDS/repo semantics
- [Bluesky docs](https://docs.bsky.app/) — API references used by `client.py`
- [Mastodon docs](https://docs.joinmastodon.org/) — the ActivityPub side
- In-repo: [docs/TOOLS.md](TOOLS.md) for the MCP tool surface · [PRD.md](../PRD.md) for the product contract
