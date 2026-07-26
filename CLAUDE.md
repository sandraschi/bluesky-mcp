# bluesky-mcp — Claude / agent context

Private AT Proto MCP. Ports **10760** / **10761**.

## Do

- Queue fleet-PR drafts via outbox; require human approve before publish
- Keep `BLUESKY_DRY_RUN=1` unless Sandra explicitly wants a live post
- Follow FLEET_PROMOTION.md tone

## Don't

- Auto-post from scraper-mcp or CI
- Call Bluesky API from fleet-public-relations-mcp (handoff only)
- Add GitHub Actions while `.nopublish` / private
- Bluesky here

## Commands

```powershell
.\start.ps1
uv run pytest tests/ -q
just mcpb-pack
```

See AGENTS.md, PRD.md, llms-full.txt.
