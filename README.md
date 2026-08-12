# clockify-python-115

Complete async Python SDK for the Clockify API plus an MCP server.

- `clockify` — async SDK: all 168 Clockify operations through 29 explicit resources.
- `clockify_mcp` — MCP server: read-only Clockify tools over stdio (`clockify-mcp`).

```bash
uv add clockify-python-115          # SDK
uv add "clockify-python-115[mcp]"   # SDK + MCP server
```

## SDK quickstart

```python
import asyncio, os
from clockify import ClockifyClient

async def main():
    async with ClockifyClient(
        api_key=os.environ["CLOCKIFY_API_KEY"],
        workspace_id=os.environ.get("CLOCKIFY_WORKSPACE_ID"),
    ) as clockify:
        me = await clockify.users.me()
        projects = await clockify.projects.list(archived=False)
        tag = await clockify.tags.create({"name": "example"})
        await clockify.tags.delete(tag.id)

asyncio.run(main())
```

- Exactly one credential: `api_key` (header `X-Api-Key`) or `addon_token`
  (`X-Addon-Token`). Never both.
- All 168 operations are explicit typed methods on 29 resources; a bounded
  `client.raw.call(operation_id, ...)` escape hatch exists for advanced use.
- No write is ever automatically retried. A transport failure during a mutation
  raises `MutationOutcomeUnknownError`: read state back before retrying by hand.
- Several `PUT` operations fully replace the entity — resend fields you must
  keep (see `docs/api-deviations.md`).

## MCP server

`clockify-mcp` serves 60 read-only Clockify tools plus 5 workflows over stdio.
It is structurally read-only; see `docs/mcp.md`.

## Docs

- `docs/architecture.md` — module layout and boundaries
- `docs/api-deviations.md` — proven Clockify quirks this SDK encodes
- `docs/mcp.md` — MCP configuration and tool list
- `docs/live-tests.md` — sacrificial-workspace live suite rules
