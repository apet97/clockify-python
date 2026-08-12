# Implementation status

## Goal
Complete Clockify Python SDK (`clockify`) + MCP (`clockify_mcp`) per `docs/port/` blueprints.
Distribution `clockify-python-115`, console `clockify-mcp`.

## Blueprint hashes (verified 2026-08-12)
- MASTER_IMPLEMENTATION_PLAN.md `98cd9d52…83f9513` ✓
- OPERATION_PORT_MANIFEST.md `c980a24f…30e2846` ✓
- MCP_WRITE_SAFETY_PLAN.md `f278b1dd…200311` ✓
- Corrected OpenAPI `38b6dcda…016d3d94` ✓ (at `../clockify-ts-sdk/spec/corrected/`)

## Reference repo
- `../clockify-ts-sdk` HEAD `d7091a44a1b95d4918fa17a7f9b174bf668a9136` (equals plan anchor).
- Initial tracked status: clean (no tracked modifications).

## Current phase
COMPLETE (2026-08-12). All ten phases implemented; final gates green; wheel
smokes green; live suite green with zero residue. MCP writes: safety core +
wave-1 adapter proven; release registration remains read-only because two ship
conditions are structurally unmeetable here (independent human review, two real
host approval-UI proofs).

## Design decisions worth knowing (deviations documented)
- ReadOnlyExecutor lives in clockify._transport.executor (re-exported by
  clockify_mcp.read_executor) so the SDK enforces it without importing MCP code.
- MCP raw read tools dispatch via client.raw.call (registered op IDs only, same
  ReadOnlyExecutor) instead of resource methods, so ReadResult can carry
  request_id + Last-Page; workflows use resource methods.
- Multipart ops with no file send form fields as filename-less multipart parts
  (updateExpense stays multipart/form-data — proven in wiring tests).
- Retry policy lives in config.py + executor (no separate retry.py).

## Completed phases
- Phases 4-5 (adb992e): 29 resource modules / 168 explicit methods, 168-op wiring suite
  (tests/contract/wiring/, COVERED completeness test), pagination.py + money.py + deviation
  regressions (tests/contract/test_known_deviations.py).
- Phases 6-7 (95b2fb8): read MCP — 60 raw tools (27 domain modules under
  clockify_mcp/tools/), 5 workflows, ReadOnlyExecutor boundary tests, in-memory MCP tests,
  real stdio smoke (65 tools listed), shared-report JSON/CSV-only pre-network rejection.
- Phase 1 skeleton (commit 4f81dcd): pyproject/uv/ruff/pyright/pytest/ci, wheel smoke green.
- Phase 2 models (c317786 + tests): importer `scripts/import_openapi.py` (fail-closed),
  339 roots → 30 domain modules + explicit __init__; request extra=forbid /
  response extra=allow proven; importer fixture tests.
- Phase 2 registry + Phase 3 transport (ee38c60): 168 hand-authored Operation records in
  29 domain modules (six extraction subagents, main-thread verified against spec —
  tests/contract/test_complete_surface.py all green incl. byte-exact path/query check);
  HttpExecutor + ReadOnlyExecutor + auth/hosts/encode/decode + raw escape hatch;
  45 transport tests (retry boundary incl. GET-write trap, outcome-unknown, cancellation,
  redirects refused, custom-host opt-in, multipart, content-negotiation).
  Wiring fixtures for Phase 4 at tests/fixtures/wiring/*.json (168 ops, request/response
  model names + deviation notes).
- Phase 0 (spike scripts deleted; conclusions below). Counts verified from spec+manifest:
  168 ops, 62 non-mutating (49 GET + 13 POST), 106 mutating, hosts 157/10/1,
  exactly 3 multipart (uploadImage, createExpense, updateExpense — spec omits the
  expense request bodies; manifest is authoritative), 339 reachable schema roots
  (closure must traverse components/parameters+responses+requestBodies), 6 unreachable
  schemas match manifest. All (resource, method) pairs unique, none a Python keyword.

### Phase 0 MCP v2 seam facts (mcp 2.0.0, pydantic 2.13.4)
- Imports: `from mcp.server import MCPServer`; `from mcp.server.mcpserver import Elicit, Resolve`;
  `from mcp.server.request_state import RequestStateSecurity` (kwargs `keys=[32B]`,
  `bind_principal=fn(ctx)->str|None`, `ttl`); pass as `MCPServer(request_state_security=...)`.
- Tool registration: `@server.tool()`; resolver params must be tool-argument names,
  `Context`, or nested `Resolve`. Resolved params stay out of `tool.input_schema` (proven).
- In-memory testing: `mcp.Client(server, elicitation_callback=..., mode="legacy"|"auto")`;
  high-level `client.call_tool` drives MRTR rounds; low-level
  `client.session.call_tool(..., allow_input_required=True, input_responses={id: {...}},
  request_state=...)` exposes raw rounds. `InputRequiredResult.input_requests` maps id→request.
- PROVEN: byte-identical `request_state` replay passes integrity and dispatches the tool
  body twice → server-side atomic nonce store is mandatory (plan confirmed).
- PROVEN: legacy mode (`mode="legacy"`) resolves the same Elicit resolver.
- PROVEN: real stdio (`server.run(transport="stdio")` + `mcp.client.stdio.stdio_client`)
  keeps stdout protocol-clean while server logs to stderr.
- Pydantic seams proven: alias round-trip incl. `page-size`, extra forbid/allow with
  `model_extra`, RootModel arrays, None-vs-unset serialization split.

## Last known green commands (2026-08-12)
- uv run ruff check . / ruff format --check . / pyright  → clean
- uv run pytest -q -m "not live"  → 397 passed
- uv run pytest -q -m live  → 5 passed (see Live-test runs)
- uv build; wheel[mcp] install into clean venvs (3.14 + 3.11): SDK import,
  `clockify-mcp --help`, and real stdio list_tools (65) all green.

## Current work in progress
(none — implementation complete)

## Completed phases (later)
- Phase 8 (689bdaf, 6201ee0): write-safety core (canonical/plan/nonce/gate/
  executor/reconcile), 62 adversarial tests, fresh-context adversarial review at
  docs/mcp-write-safety-review.md; all findings (P,A,B,C,T,X,D,E) fixed.
- Phase 9 wave 1 (4de8c4b): clockify_tags_create through the full gate;
  build_approved_server separate from the shipped read-only server; live Phase G
  proof green, zero residue. Later waves deliberately deferred: each write needs
  individual review and host-UI evidence per plan; batching them is forbidden.
- Phase 10: docs (architecture/api-deviations/mcp/live-tests), README,
  CHANGELOG, examples/sdk_quickstart.py, uv build, clean-venv wheel[mcp] smokes
  (3.14 + 3.11), console + real-stdio smoke (65 tools), live suite 6/6.

## Unresolved evidence questions / real blockers
- Target-host human-approval UI evidence (2 real hosts) — unmet ship condition,
  requires interactive host products; MCP writes stay unregistered.
- Several PUT omission rules remain UNKNOWN_CONSERVATIVE per manifest.

## Live-test runs
- Run 2026-08-12, prefix `py115-<random>` (fresh per run): me/workspace identity,
  read smoke, Last-Page header, tag create→get→full-replace-archive→delete,
  project create→delete-403-proof→archive→delete. Residue: 0 (asserted in-suite).

## Material deviations from blueprint
- Live workspace shapes: `features` enum open; `entityCreationPermissions`
  values plain strings → importer STR_UNION_REFS + regression test (f510d21).
- See "Design decisions worth knowing" above for structural choices.

## Next exact action
Nothing pending in-code. Remaining work is external: (1) independent human
adversarial review of clockify_mcp/writes; (2) approval-UI evidence on two real
MCP hosts; (3) then wave-2+ write adapters one reviewed tool at a time; (4)
optional PyPI publish via explicit release workflow (never done automatically).


