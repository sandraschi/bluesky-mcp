# GitHub Copilot instructions for bluesky-mcp

FastMCP 3.4+ Bluesky (AT Proto) bridge with a human-approved outbox for fleet-PR drafts.
Dry-run default: posts are never live until a human approves them in the outbox.

## Session Context (Bluesky MCP)

You have access to Bluesky posting, timelines, notifications, and a human-gated outbox.

**Before starting work:**
1. Check pending drafts: `bluesky_social_tool(operation="outbox_list")`
2. Review notifications: `bluesky_social_tool(operation="notifications")`

**At end of work:**
- Queue new drafts for approval: `bluesky_social_tool(operation="outbox_enqueue", status_text="...")`
- Publish only after `outbox_approve` — never direct `post` for fleet promotion.
