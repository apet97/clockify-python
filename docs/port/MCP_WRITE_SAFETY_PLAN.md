# MCP write safety: the shipped mechanism

This document describes the write-safety system that ships in
`clockify_mcp` 0.2.0. It replaced the pre-ship plan of the same name after
the owner approved registering the full write surface. The invariants below
are enforced in code and pinned by tests; this text is descriptive, not
aspirational.

## Tiers

`clockify_mcp.risk.RISK_BY_TOOL` classifies every registered tool. The tier
decides behavior:

| Tier | Behavior |
|---|---|
| `read` | Dispatches through `ReadOnlyExecutor`; cannot mutate. |
| `routine_write` | Executes directly. Single attempt, never retried. |
| `business_write`, `external_side_effect`, `privileged`, `destructive` | Sealed approval gate (below). |

Routine tools are limited to personal time-entry operations and the
daily-tracking workflows. `tests/mcp/test_full_surface.py` pins the map to
the registered surface exactly.

## The sealed gate

Every guarded write runs the same pipeline (`clockify_mcp.writes.runner`):

1. **Prepare** — the tool compiles the exact wire request(s) into an
   immutable `WritePlan`: operation ids, path arguments, query pairs, and
   canonical JSON body bytes. The plan digest covers all of it.
2. **Preview** — `render_preview` shows the user every bound step: method,
   path, arguments, and body, plus effect, scope, reversibility, and
   warnings. The preview is deterministic.
3. **Approval** — the user decides through the MCP sealed request-state
   mechanism (`RequestStateSecurity`; Multi Round-Trip Requests on spec
   2026-07-28, synchronous elicitation on legacy hosts). The approval is a
   resolved parameter: the model never sees or supplies it. Hosts without
   approval support fail closed — guarded writes cannot execute there.
4. **Consume** — a single-use nonce (atomic, TTL 300 s, tombstoned) is bound
   to principal + tool + arguments digest + workspace + plan digest.
   Replays and drifted arguments refuse before any dispatch.
5. **Revalidate** — the consumed plan's shape is re-checked against the
   tool's expected operations; bodies re-validate against the SDK request
   model. A malformed plan never dispatches.
6. **Recheck** — tools with preconditions re-read current state; drift after
   approval refuses the write (the nonce is already burned).
7. **Dispatch** — `ControlledWriteExecutor` sends only the stored plan's
   steps, in order, comparing each recompiled request digest byte-for-byte.
   Nothing retries. A mid-plan failure is terminal and reports
   `partial_failure` with the exact applied steps.
8. **Reconcile** — optional read-back through the read-only client;
   a failed read-back yields `succeeded_unreconciled`, never a retry.

Result states: `rejected`, `failed_before_dispatch`, `failed`,
`partial_failure`, `outcome_unknown`, `succeeded`, `succeeded_unreconciled`,
`reconciled`.

## Tool-specific hardening

- Webhook create/update validate the target URL offline (HTTPS only; no
  loopback, private, link-local, or metadata destinations) and redact the
  returned `authToken` from every receipt.
- `clockify_demo_cleanup` discovers only `DEMO-`/`sdk-demo-` prefixed
  entities across full pagination, encodes archive-before-delete and
  DONE-before-delete prerequisites as ordered steps in ONE approved plan,
  and re-checks the prefix rule at revalidation.
- Bulk writes canonicalize their ID sets and refuse above 1,000 items.
- File-bearing writes are not exposed: `uploadImage` has no tool and expense
  tools carry no file part.

## Test map

- `tests/mcp/writes/test_runner.py` — multi-step order, partial failure,
  replay, revalidation refusal, routine tier read-op refusal.
- `tests/mcp/writes/test_domain_tools.py` — one wiring proof per write tool:
  approval dispatches the exact request once; rejection dispatches nothing.
- `tests/mcp/writes/test_wave1_tags_create.py` — end-to-end gate lifecycle
  including preconditions, drift, replay, and read-only separation.
- `tests/mcp/writes/test_nonce_store.py`, `test_controlled_executor.py`,
  `test_gate_resolver.py`, `test_canonical_and_plan.py`,
  `test_workspace_binding.py`, `test_plan_size_bounds.py` — the gate core.
- `tests/mcp/test_workflows_write.py` — workflow behavior including SSRF
  refusal, prefix refusal, and archive-then-delete ordering.
- `tests/mcp/test_http_transport.py` — a gated write approved end-to-end
  over Streamable HTTP.

## Live rules

Write experiments run only against a verified sacrificial workspace, with
unique prefixes, exact-ID cleanup in `finally`, and zero-residue checks
(`tests/live/`).
