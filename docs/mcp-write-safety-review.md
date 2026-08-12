# MCP Write-Safety Gate — Adversarial Review

**Reviewer:** fresh-context, same-vendor AI subagent (Claude). NOT the author of this
code. This is **not** independent human approval. The plan's final ship condition
"An independent adversarial reviewer approves the implementation" (Conditions
checklist, `docs/port/MCP_WRITE_SAFETY_PLAN.md`) remains **UNMET** by this review.

**Date:** 2026-08-12
**Scope:** `src/clockify_mcp/writes/{canonical,plan,principal,nonce_store,gate,executor,reconcile,state}.py`
and the existing suite `tests/mcp/writes/` (60 tests, all passing).
**Method:** read the plan invariants W-01..W-16 and the source line by line; wrote and
ran adversarial probe tests. Two findings are kept as durable strict-`xfail`
regression guards in `tests/mcp/writes/test_plan_size_bounds.py` — they assert the
CORRECT behavior, fail today (documenting the live defect), and flip to a hard
suite failure the moment the defect is fixed. The remaining probes were run inside
the test tree (`asyncio_mode=auto`) and are reproduced inline below.

## Findings table

Ordered by risk. The preview↔binding gap (P) leads because the entire model rests
on the one thing the server admits it cannot prove: that a human read and understood
the preview. That is the layer with the real defect.

| # | Severity | Invariant / plan clause | Status | Summary |
|---|----------|-------------------------|--------|---------|
| P | blocker | Deterministic preview contract; Phase A acceptance; W-03 | CONFIRMED | `render_preview` never shows the bound wire body, path arguments, target identity, or result — the human approves a preview that does not reflect what dispatches. |
| A | major | Nonce store bounds (plan "max 256 KiB canonical plan size per record"; W-08 store integrity) | CONFIRMED | `_plan_size` omits `warnings`, `summary`, `title`, `preconditions`, and file-digest metadata, so the per-record byte cap is bypassable by orders of magnitude. |
| B | minor | Nonce-store contract / W-06, W-16 | CONFIRMED | `get_or_issue` reuse branch trusts `key` alone and silently drops the caller's `principal_id`/`workspace_id`/`arguments_digest`; `workspace_id` is also absent from the key and hidden in the preview. |
| C | minor | Atomic consume "constant-time where appropriate" | CONFIRMED | `tool_name` compared with `==` while the three other bindings use `hmac.compare_digest`. Low impact (tool name is not secret) but inconsistent with the stated rule. |
| T | minor | Deterministic preview contract | CONFIRMED | `render_preview` hardcodes `Valid for: 5 minutes` while `ttl` is configurable — the approval UI misstates the window when `ttl != 300`. |
| X | minor | Controlled executor / W-05 | CONFIRMED | `dispatch` sends the caller-supplied `step`, not the approved one; safe only because `request_digest` currently covers every `WriteStep` field. Adding a field to `WriteStep` without adding it to the digest would open a direct injection past the gate. |
| D | note | W-05 exact-plan binding | CONFIRMED | `WritePlan.digest` omits `reconciliation`. Not material (read-only, post-dispatch, permit carries the stored plan), but worth an explicit comment. |
| E | note | Controlled executor checklist | CONFIRMED | `_validate` does not re-verify `principal`/`tool` against the permit or check destination host. Not exploitable: service host is bound inside `request_digest` and principal/tool are bound at `consume`; defence-in-depth only. |

The core single-use, atomic-consume, exact-digest, and terminal-state properties
(W-04, W-05, W-07, W-08, W-09, W-11) held under every probe I ran. But finding P is
blocker-class for shipping: an unenforced preview contract defeats the human-approval
assurance the plan explicitly says the server cannot provide by itself.

## Detail

### P — Preview does not show what dispatches (blocker, CONFIRMED)

`src/clockify_mcp/writes/plan.py:127-155` (`render_preview`) renders `title`,
`summary`, `effect`, `scope`, `reversibility`, and free-text `preview_fields` /
`warnings`. For each step it emits only `operation.http_method` and
`operation.path` (`plan.py:140-142`). It never renders `step.body_json`,
`step.path_arguments`, `step.query`, the target entity identity, or the result —
all of which the plan's "Deterministic preview contract" requires
(`Approved request fields: <exact redacted diff/body>`, `Target:`,
`Result if complete:`). Phase A acceptance ("previews are deterministic and redact
secrets") is not met as written.

`plan.digest` DOES cover the body, so the preview text cannot drift after approval —
but **bound is not the same as accurate**. A plan builder can bind a body the
preview never shows, and the human approves it. Demonstrated: a plan whose
`body_json` is `{"name":"evil","archived":true}` with `preview_fields=[("Name","harmless")]`
renders an approvable preview reading `Name: harmless` / `Summary: harmless` — the
words `evil` and `archived` never appear. Full rendered preview from the probe:

```
Action: Create tag
Confirmation ID: nnnnnnnnnnnn
Workspace: (user default)
Summary: harmless
Effect: create
Scope: one
Reversibility: reversible
Steps:
  1. POST /workspaces/{workspaceId}/tags (postWorkspacesWorkspaceIdTags)
Details:
  Name: harmless
Valid for: 5 minutes
Decision: approve or reject
```

Today builders are server-side, so a *model* cannot set these strings directly; the
exposure is (1) any builder that summarizes a body imperfectly, and (2) the invariant
simply not holding, which every future write tool inherits. **Recommended fix:**
render the canonical, redacted body directly from `step.body_json` (and path/query)
inside `render_preview`, or enforce a builder-side invariant that every body key
appears in `preview_fields`. Guarded by the strict-`xfail`
`test_preview_should_show_bound_body`.

### A — Per-record plan-size cap is bypassable (major, CONFIRMED)

### A — Per-record plan-size cap is bypassable (major, CONFIRMED)

`src/clockify_mcp/writes/nonce_store.py:92-102` (`_plan_size`) sums only:
step `body_json`, step `path_arguments`, `query`, `multipart_fields`, and
`preview_fields`. It never counts `WritePlan.warnings`, `.summary`, `.title`,
`.effect`, `.scope`, `.sensitivity`, `.reversibility`, `Precondition.description`,
or the file-digest strings. The plan (`MCP_WRITE_SAFETY_PLAN.md`, "Nonce store /
Scope and bounds") states the store enforces a "maximum 256 KiB canonical plan
size per record" whose purpose is to "prevent unbounded memory growth."

Because these fields are not counted, a record whose true canonical size is
> 1 MiB passes a 4 KiB cap. Demonstrated:

- 1 MiB `warnings` string accepted under `max_plan_bytes=4096`
  (canonical warnings alone = 1,048,607 bytes).
- 512 KiB `summary` accepted under the same cap.
- 512 KiB `Precondition.description` accepted under the same cap.
- 128 pending records each carrying ~1 MiB warnings are retained simultaneously
  (`max_pending=128`), so resident memory reaches ~128 MiB while the intended
  bound implied by 128 × 256 KiB is ~32 MiB — a ~4× (unbounded per field) blow-up.

Where these plan fields come from matters for exploitability: `title`, `summary`,
`warnings`, and precondition descriptions are produced by server-side plan
builders, so a *model* cannot set them directly today. The risk is (1) a plan
builder that echoes untrusted Clockify response text (names/descriptions —
explicitly listed as untrusted input in the plan's Trust model) into
`summary`/`warnings`, giving a remote actor a memory-amplification lever, and
(2) the invariant simply not holding as written, which a future write tool could
trip. The `max_pending` cap still bounds record *count*, so this is DoS-flavoured,
not a bypass of single-use.

**Recommended fix:** compute size from the actual canonical serialization, e.g.
`len(canonical_json(plan_material)) ` using the same material dict that
`WritePlan.digest` already builds (extended to include every stored field), or
extend `_plan_size` to add `title`, `summary`, `effect`, `scope`, `reversibility`,
each `sensitivity` entry, each `warning`, each precondition `description`/`fingerprint`,
and each `FileDigest` field. Add boundary tests over `warnings`/`summary`/`preconditions`,
not only over step `body_json` (the current `test_plan_byte_boundary` only exercises
the body path). Guarded by the strict-`xfail` `test_huge_warnings_should_hit_byte_cap`.

### B — Reuse branch trusts `key` and drops caller bindings (minor, CONFIRMED)

`src/clockify_mcp/writes/nonce_store.py:119-121`: when a pending record exists for
`key` with a matching `plan_digest`, the stored record is returned verbatim and the
caller's freshly supplied `principal_id`, `workspace_id`, and `arguments_digest`
are ignored. Demonstrated: caller passing `principal="mallory", workspace="wsB"`
receives a record still stamped `alice`/`wsA`.

This is safe end-to-end because `WriteGate.derive_key` (`principal.py:30`) binds
`principal_id`, `tool_name`, and `arguments_digest` into the HMAC key, and
`consume` re-verifies all bindings. But `workspace_id` is **not** in the key
material, so two calls that differ only by workspace share a key; they are
separated today only because the workspace appears in step path-arguments and
therefore changes `plan_digest`. If a future write plan ever carries the workspace
outside the digested step components, the reuse branch would hand back a record
bound to the wrong workspace. This is already partly user-visible: `render_preview`
(`plan.py:132`) renders `prepared.workspace_id or '(user default)'`, so a `None`
workspace means the human approves a mutation without seeing which workspace it
targets — the same root cause seen from the preview side. **Recommended fix:**
either assert the reuse-branch record matches the passed
`principal_id`/`workspace_id`/`arguments_digest` (fail closed on mismatch), or fold
`workspace_id` into `derive_key`; and render the resolved workspace in the preview.

### C — Non-constant-time `tool_name` comparison (minor, CONFIRMED)

`src/clockify_mcp/writes/nonce_store.py:180`: `record.tool_name == tool_name`
alongside three `hmac.compare_digest` calls. The plan's "Atomic consume" section
says "compare every binding in constant-time where appropriate." Tool name is not
a secret, so timing leak is immaterial, but for consistency use
`hmac.compare_digest(record.tool_name, tool_name)`.

### T — Hardcoded validity window in the preview (minor, CONFIRMED)

`src/clockify_mcp/writes/plan.py:153` emits the literal `Valid for: 5 minutes`
while the store TTL is configurable (`nonce_store.py:68`, `ttl: float = 300.0`).
Set `ttl=60` and the approval UI tells the user "5 minutes" for a 60-second window.
In a gate whose whole assurance is that the human read an accurate preview, a
misstated validity window is a real (if small) defect. `prepared.expires_at -
prepared.issued_at` gives the true window; render it.

### X — Executor dispatches the caller's step object (minor, CONFIRMED)

`src/clockify_mcp/writes/executor.py:85`: after `_validate` compares digests,
`dispatch` sends `self._sender(step)` — the caller-supplied object, not the approved
`self._permit.plan.steps[step_index]`. This is safe **today only because**
`WriteStep.request_digest` happens to cover all five step fields (operation_id,
path_arguments, query, body sha256, multipart_fields, and every `FileDigest`
field). The day someone adds a field to `WriteStep` without adding it to the digest
material, this becomes a direct injection path past an approval gate. One-line
hardening: dispatch the approved step (`self._permit.plan.steps[step_index]`), not
the caller's. This is the concrete mechanism behind Finding E's "self-contained
executor" argument.

### D — `reconciliation` absent from `WritePlan.digest` (note, CONFIRMED)

`src/clockify_mcp/writes/plan.py:91-105`: the digest material excludes the
`reconciliation` field. Not a safety gap — reconciliation is read-only and runs
post-dispatch from the permit's stored plan object, not from a re-supplied value —
but the omission should be documented so a later change that makes reconciliation
behaviour security-relevant does not silently escape the digest.

### E — Executor omits principal/tool/host re-checks (note, CONFIRMED)

`src/clockify_mcp/writes/executor.py:51-79` (`_validate`) checks terminal state,
step order, operation id, mutating semantics, and `request_digest`. The plan's
"Controlled executor" checklist also lists "principal and tool match" and
"destination host is valid." These are not re-checked here. Not exploitable:
`service.value` is inside `request_digest` (so host is bound), and principal/tool
are bound at `consume`. Treat as defence-in-depth: an explicit
`permit.principal_id`/`permit.tool_name` assertion would make the executor
self-contained rather than relying on an upstream invariant.

## What held up under attack

- Single-use: 100 concurrent `consume` calls yield exactly one permit (existing
  test `test_hundred_concurrent_consumers_yield_one_permit`), and the tombstone
  rejects replay with `confirmation_already_used`.
- Changed plan invalidates the old nonce; the old confirmation cannot consume.
- Digest binds method/service/path/query/body-sha256/multipart/files; a changed
  request byte flips `request_digest` and the executor marks the permit terminal.
- `is_approved` fails closed for a plain `dict` payload (attribute access, not key
  access) and for any `action != "accept"`.
- Method cannot be overridden per step: `WriteStep` has no method field; method is
  read from the registry keyed by `operation_id`, which is itself in the digest.
- Expiry removes the record; terminal executor state sticks across dispatch,
  cancellation, and any exception.

## Ship-condition statement

This review is an AI subagent pass from the same vendor as the implementation. It
does **not** satisfy the plan's mandatory condition of independent adversarial
**human** approval, and it does not touch the other unchecked ship conditions
(pinned modern/legacy resolver tests, two real hosts, live sacrificial-workspace
proof, etc.). Write-tool registration must remain disabled. Fix Finding P (blocker) and Finding A
(major) before any further write-safety sign-off; B/C/T/X are low-cost hardening;
D/E are documentation / defence-in-depth. Findings P and A are pinned by strict-`xfail`
regression guards in `tests/mcp/writes/test_plan_size_bounds.py`.

## Post-review fixes (2026-08-12, applied by the implementation session)

- P: `render_preview` now renders every step's exact bound path arguments,
  query pairs, canonical body, multipart fields, and file digests; guarded by
  `test_preview_should_show_bound_body` (now a normal passing test).
- A: `_plan_size` counts every stored string (title/summary/effect/scope/
  reversibility/sensitivity/warnings/preconditions/file digests); guarded by
  `test_huge_warnings_should_hit_byte_cap`.
- B: `get_or_issue` reuse branch verifies principal/tool/workspace/arguments
  against the stored record and fails closed; `workspace_id` folded into
  `derive_key`.
- C: `tool_name` compared with `hmac.compare_digest` in `consume`.
- T: preview renders the real validity window from `expires_at - issued_at`.
- X: `ControlledWriteExecutor.dispatch` sends the permit's stored step object,
  never the caller's.
- D/E: documented in code comments at the digest and executor validation sites.

Ship conditions still unmet (unchanged): independent human adversarial review
and two real target-host approval-UI proofs. Write registration stays absent.
