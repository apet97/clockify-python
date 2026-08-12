# Repository maintenance guide

This repository implements `clockify-python-115`. Use current source and tests
as executable evidence. Use the three plans in `docs/port/` for the intended
contract:

- `MASTER_IMPLEMENTATION_PLAN.md`: architecture and release gates.
- `OPERATION_PORT_MANIFEST.md`: all 168 operation records and public mappings.
- `MCP_WRITE_SAFETY_PLAN.md`: mandatory write-safety conditions.

The read-only evidence repository is `../clockify-ts-sdk` at commit
`d7091a44a1b95d4918fa17a7f9b174bf668a9136`. Do not modify it.

## Architecture map

- Operation: `src/clockify/operations/<domain>.py`
- Model: `src/clockify/models/<domain>.py`
- Public SDK method: `src/clockify/resources/<domain>.py`
- Request and response boundary: `src/clockify/_transport/`
- MCP read tool: `src/clockify_mcp/tools/<domain>.py`
- MCP workflow: `src/clockify_mcp/workflows/`
- Dormant write safety: `src/clockify_mcp/writes/`

Add one explicit operation record, method, tool decision, and focused test.
Do not add runtime method generation or generic CRUD machinery.

## Read-only boundary

The default server must expose exactly 60 raw reads and five workflows. It must
register zero writes and import no write module. Every MCP read path must use
`ReadOnlyExecutor`. Tool annotations are not enforcement.

Do not register a write until every condition in `MCP_WRITE_SAFETY_PLAN.md`
passes, including independent review and approval-UI evidence in two intended
hosts.

## Gates

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q -m "not live"
uv build
```

CI and release checks must clone the evidence repository at the pinned commit.
They must not set `CLOCKIFY_ALLOW_MISSING_TS_SDK_EVIDENCE`.

## Hard stops

Stop and gather evidence if a route, schema, money unit, replacement rule, or
write outcome is uncertain. Never retry a write automatically. Never expose an
arbitrary URL or method. Never put a credential in source, logs, errors, tests,
or artifacts. Do not push, tag, publish, or change a remote unless the owner
explicitly asks.
