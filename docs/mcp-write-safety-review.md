# MCP Write-Safety Gate — Adversarial Review

**Reviewer:** fresh-context, same-vendor AI subagent (Claude). NOT the author of this
code. This is **not** independent human approval. The plan's final ship condition
"An independent adversarial reviewer approves the implementation" (Conditions
checklist, `docs/port/MCP_WRITE_SAFETY_PLAN.md`) remains **UNMET** by this review.

**Date:** 2026-08-12
**Scope:** `src/clockify_mcp/writes/{canonical,plan,principal,nonce_store,gate,executor,reconcile,state}.py`
and the existing suite `tests/mcp/writes/` (60 tests, all passing).
**Method:** read the plan invariants W-01..W-16 and the source line by line; wrote and
ran adversarial probe tests. The probe file lives at
`scratchpad/test_probe.py` (session scratchpad) — it was run inside the test tree
with `asyncio_mode=auto` and then removed so no green test masquerades as a
regression guard for a live defect.

## Findings table

| # | Severity | Invariant / plan clause | Status | Summary |
|---|----------|-------------------------|--------|---------|
| A | major | Nonce store bounds (plan "max 256 KiB canonical plan size per record"; W-08 store integrity) | CONFIRMED | `_plan_size` omits `warnings`, `summary`, `title`, `preconditions`, and file-digest metadata, so the per-record byte cap is bypassable by orders of magnitude. |
| B | minor | Nonce-store contract / W-06, W-16 | CONFIRMED | `get_or_issue` reuse branch trusts `key` alone and silently drops the caller's `principal_id`/`workspace_id`/`arguments_digest`. End-to-end safe only because `consume` re-checks; store contract is weaker than its record fields imply. |
| C | minor | Atomic consume "constant-time where appropriate" | CONFIRMED | `tool_name` compared with `==` while the three other bindings use `hmac.compare_digest`. Low impact (tool name is not secret) but inconsistent with the stated rule. |
| D | note | W-05 exact-plan binding | CONFIRMED | `WritePlan.digest` omits `reconciliation`. Not material (read-only, post-dispatch, and the permit carries the stored plan object), but worth an explicit comment. |
| E | note | Controlled executor checklist | CONFIRMED | `_validate` does not re-verify `principal`/`tool` against the permit or check destination host, unlike the plan's executor checklist. Not exploitable: service host is bound inside `request_digest` and principal/tool are bound at `consume`; this is defence-in-depth only. |

No blocker was found. The core single-use, atomic-consume, exact-digest, and
terminal-state properties (W-04, W-05, W-07, W-08, W-09, W-11) hold under the
probes I ran.

## Detail

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
the body path).

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
bound to the wrong workspace. **Recommended fix:** either assert the reuse-branch
record matches the passed `principal_id`/`workspace_id`/`arguments_digest` (fail
closed on mismatch), or fold `workspace_id` into `derive_key`.

### C — Non-constant-time `tool_name` comparison (minor, CONFIRMED)

`src/clockify_mcp/writes/nonce_store.py:180`: `record.tool_name == tool_name`
alongside three `hmac.compare_digest` calls. The plan's "Atomic consume" section
says "compare every binding in constant-time where appropriate." Tool name is not
a secret, so timing leak is immaterial, but for consistency use
`hmac.compare_digest(record.tool_name, tool_name)`.

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
proof, etc.). Write-tool registration must remain disabled. Fix Finding A before
any further write-safety sign-off; B/C are low-cost hardening; D/E are documentation
/ defence-in-depth.
