# clockify-python — repository guide for Claude

This repository implements the complete Clockify Python SDK + MCP described by three
authoritative blueprints. Do not re-plan. Read them, then continue from
`IMPLEMENTATION_STATUS.md` → "Next exact action".

## Authoritative inputs (do not copy content out of them)

- `docs/port/MASTER_IMPLEMENTATION_PLAN.md` — architecture, phases, gates, implementer contract.
- `docs/port/OPERATION_PORT_MANIFEST.md` — all 168 endpoint records and public resource/method map.
- `docs/port/MCP_WRITE_SAFETY_PLAN.md` — every MCP mutation-safety invariant and ship condition.
- Evidence only (READ-ONLY, never modify): `../clockify-ts-sdk` at HEAD
  `d7091a44a1b95d4918fa17a7f9b174bf668a9136`; corrected OpenAPI at
  `../clockify-ts-sdk/spec/corrected/clockify.corrected.openapi.yaml`.

## Write boundary

Create/edit/delete ONLY inside this directory (`2mcp`). OS temp dirs are fine for
disposable wheel-install tests. Never touch `../clockify-ts-sdk` or anything else
under `addons-me`. Never commit secrets (`.env` is gitignored).

## Non-negotiable architecture

- Distribution `clockify-python-115`; imports `clockify` + `clockify_mcp`; console `clockify-mcp`;
  Python >= 3.11; hatchling; uv; MCP deps behind `[mcp]` extra.
- Async-only `ClockifyClient`, one reused `httpx.AsyncClient`, exactly one credential
  (`api_key` XOR `addon_token`), final-host validation before auth, redirects disabled.
- Exactly 168 operations / 29 resources / 168 explicit public methods / 62 reads (49 GET +
  13 POST) / 106 writes / 339 reachable model roots / 60 raw MCP read tools / 5 workflows.
- Static hand-authored operation records in 29 domain modules; static committed Pydantic v2
  models; no runtime generation, no `__getattr__`, no import-time registration side effects.
- Every MCP read path goes through the final-boundary `ReadOnlyExecutor`.
- No write auto-retry ever. MCP writes ship only per the safety plan; default server stays
  structurally read-only.

## Startup/resume ritual (every fresh session)

1. `pwd -P`; confirm project and `../clockify-ts-sdk` paths.
2. Read this file, then `IMPLEMENTATION_STATUS.md`.
3. Read the master-plan section for the current phase.
4. `git status --short` and `git log --oneline -5`.
5. Verify sibling repo unchanged: `git -C ../clockify-ts-sdk status --short` (must be clean)
   and HEAD still `d7091a4`.
6. Run the narrowest green gate for the current checkpoint
   (`uv run pytest -q -m "not live"` when in doubt).
7. Continue from "Next exact action". Do not redesign completed architecture.

## Gates

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q -m "not live"
uv build
```

Live suite (sacrificial workspace, separate): `uv run pytest -q -m live`.
Live rules: unique run prefix, create-then-clean own artifacts only, zero residue,
never print credentials.
