# Contributing

Use Python 3.11 through 3.14. Keep changes small and explicit.

1. Read `CLAUDE.md` and the applicable plan in `docs/port/`.
2. Add or update the operation record in `src/clockify/operations/<domain>.py`.
3. Add or update the model in `src/clockify/models/<domain>.py`.
4. Add one explicit method in `src/clockify/resources/<domain>.py`.
5. Add focused request, response, and behavior tests.
6. Add an MCP read tool only for a proven non-mutating operation.
7. Do not register an MCP write without every write-safety ship condition.

Run:

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q -m "not live"
uv build
```

The corrected OpenAPI evidence repository must be a sibling checkout at commit
`d7091a44a1b95d4918fa17a7f9b174bf668a9136`. Normal and release CI must not set
`CLOCKIFY_ALLOW_MISSING_TS_SDK_EVIDENCE`.
