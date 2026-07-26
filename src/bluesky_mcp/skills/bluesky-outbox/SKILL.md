# Bluesky Outbox Skill

## Role

Hold promotion drafts from `fleet-public-relations-mcp` until a human approves, then publish to Bluesky (dry-run by default).

## Flow

1. Fleet-PR: `pr_draft` → `pr_approve_draft` → `pr_queue_fediverse`
2. This server: outbox `pending`
3. Human: Outbox UI or `outbox_approve`
4. `outbox_publish` — posts only if `BLUESKY_DRY_RUN=0`

## Tools

- `bluesky_social_tool(operation=…)` — outbox_* / timeline / notifications / accounts_list
- `bluesky_help` — ports and flow summary

## Safety

Never auto-publish. Never bypass outbox for fleet drafts.
