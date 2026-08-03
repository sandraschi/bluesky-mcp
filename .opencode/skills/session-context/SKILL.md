---
name: session-context
description: Bluesky MCP session context — check outbox + notifications before work, enqueue drafts after.
---

## Session Context (Bluesky MCP)

You can queue, approve, and publish Bluesky posts through a human-gated outbox.

**Before starting work:**
1. Check pending drafts: `bluesky_social_tool(operation="outbox_list")`
2. Review notifications: `bluesky_social_tool(operation="notifications")`

**At end of work:**
- Enqueue drafts for human approval: `bluesky_social_tool(operation="outbox_enqueue", status_text="...")`
- Never publish directly without `outbox_approve` first.
