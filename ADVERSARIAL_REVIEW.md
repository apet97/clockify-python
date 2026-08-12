# ADVERSARIAL_REVIEW.md

Independent release audit of `clockify-python-115` at commit `87e1553`.
Date: 2026-08-12 (07:00 CEST). Audit-only session: nothing was repaired.
All claims were re-derived from source, the manifest, and executable evidence —
not from `IMPLEMENTATION_STATUS.md`, commit messages, or the repo's own count tests.

Note on the audited commit: the review request named `972fd5e` as the completion
claim. The repository HEAD is `87e1553`, two commits past it
(`6c0d359` "remediate adversarial findings F1-F5 test-first" and `87e1553` docs).
This audit examined HEAD `87e1553`; the earlier findings F1–F5 from the previous
audit round are confirmed remediated at HEAD (see §6).

## Verdict

**PASS WITH EXTERNAL WRITE BLOCKERS** — the read-only release mode is ready.
Writes remain disabled pending independent human approval and real-host
approval-UI evidence per `docs/port/MCP_WRITE_SAFETY_PLAN.md`. One MEDIUM
test-gap finding (F-A below) exists in the unregistered write core and must be
repaired before any write tool is registered; it does not affect the shipped
read-only server against any external input.

## 1. Baseline (independently verified)

- HEAD `87e155398ac2a1482b6df8a9a0a7a0f4b6e611b6`, working tree clean, single ref
  `refs/heads/main`, no remotes touched.
- Blueprint SHA-256:
  - `MASTER_IMPLEMENTATION_PLAN.md` `98cd9d525d6b90d7c0f8fd72df04d4c30a43d1034d00a25d7b050cbe983f9513`
  - `OPERATION_PORT_MANIFEST.md` `c980a24fcf87c91b504a500744e1c8a3cda9b5116a78135769695d45a30e2846`
  - `MCP_WRITE_SAFETY_PLAN.md` `f278b1ddbcd846b31e31d54ccd9942b460f13bf0e5fc5e16943d0b6ded200311`
- Sibling `../clockify-ts-sdk`: HEAD `d7091a44a1b95d4918fa17a7f9b174bf668a9136`,
  status clean, never modified by this audit.
- `pyproject.toml`: distribution `clockify-python-115` 0.1.0; import packages
  `clockify` + `clockify_mcp`; console `clockify-mcp = clockify_mcp.__main__:main`;
  `requires-python >= 3.11`; hatchling; runtime deps httpx + pydantic only;
  MCP deps behind the `[mcp]` extra. Dependency direction correct: importing
  `clockify_mcp.server` loads zero `clockify_mcp.writes.*` modules
  (verified via `sys.modules` inspection), and `clockify` never imports
  `clockify_mcp`.

### Credential / .mcp.json hygiene

- `.mcp.json` exists locally, is untracked, and is listed in `.gitignore`
  (working tree reports clean).
- Reachable history: a full `git rev-list --all` tree scan finds `.mcp.json`
  in **zero** commits. No secret-bearing file in any ref.
- Dangling/reflog-only objects (reported separately, per instructions):
  `git fsck --unreachable --dangling` finds 2 unreachable commits, several
  trees, and blobs. Both unreachable commits' trees were enumerated: they
  contain only earlier revisions of `clockify_mcp` source and the safety plan —
  **no `.mcp.json`**. Every unreachable blob was content-scanned against the
  actual local secret value: zero matches. The secret value was never printed.
- Build artifacts: wheel (168 files, packages `clockify`, `clockify_mcp`,
  dist-info only) and sdist were scanned; no `.mcp.json`, no `.env`, zero
  occurrences of the secret.
- Runtime: `Credential.__repr__` redacts (`secret=<redacted>`,
  `src/clockify/_transport/auth.py:24`); the stdio probe with a fake key
  confirmed no key material in MCP error output.

## 2. Gates (all executed by the auditor)

| Gate | Result |
|---|---|
| `uv sync --all-extras --dev` | OK (45 packages resolved) |
| `uv run ruff check .` | All checks passed |
| `uv run ruff format --check .` | 246 files already formatted |
| `uv run pyright` | 0 errors, 0 warnings |
| `uv run pytest -q -m "not live"` | **421 passed, 6 deselected** |
| `uv build` | wheel + sdist built |

### Fresh-environment install proof

The exact newly built wheel (`clockify_python_115-0.1.0-py3-none-any.whl[mcp]`)
was installed into two fresh `uv venv` environments:

- Python **3.11**: `from clockify import ClockifyClient` → `ClockifyClient`;
  `clockify-mcp --help` prints usage.
- Python **3.13**: same, both pass.

### Real stdio session

The **installed** `clockify-mcp` (from the 3.11 venv, not the source tree) was
spawned over real stdio with the official `mcp` client:

- `initialize` + `tools/list` → **65 tools**: 60 raw reads + exactly the five
  workflows `clockify_status`, `clockify_workspace_overview`,
  `clockify_review_day`, `clockify_review_week`, `clockify_doctor`.
- One controlled read (`clockify_status` with an intentionally invalid key)
  executed the full dispatch path and returned a structured `is_error` result
  ("Clockify API error 401 on getCurrentUser") with no key material leaked.
- Stdout carried protocol frames only (the client session would have failed to
  parse otherwise); server logging is configured to stderr
  (`src/clockify_mcp/server.py`).

## 3. Completeness reconciliation (independent, both directions)

All numbers below were computed by introspecting
`clockify.operations.registry.ALL_OPERATIONS` and walking
`clockify.resources.*` classes with `inspect` — not by trusting count tests.

- **168** operation records, all `operation_id`s unique; every registry id
  appears in `docs/port/OPERATION_PORT_MANIFEST.md` (0 missing).
- **62 reads / 106 writes** by `semantics.mutates`; reads split **49 GET /
  13 POST** exactly.
- **29** distinct `resource` values across operations; **168** public
  non-underscore resource methods discovered across resource modules;
  `(resource, sdk_method)` pairs are all unique (168), every operation's
  `sdk_method` resolves to exactly one existing public method, and there are
  **zero** public resource methods without a backing operation (168 − 168 = 0).
- Service routing: `regular` **157**, `reports` **10**, `audit_log` **1**.
- Multipart: exactly **3** (`createExpense`, `updateExpense`, `uploadImage`).
- GET-verb operations classified as writes: **none exist** in the registry
  (checked explicitly; the no-write-retry invariant therefore has no GET-verb
  edge case to defend, and verb-based retry shortcuts would still be caught by
  the `mutates`-based gate — see mutant M2).
- MCP surface: 60 raw read tools registered exactly once via explicit per-domain
  `register()` calls in `src/clockify_mcp/tools/__init__.py` (no decorator
  scanning, no import-time side registration); 5 workflows; live `tools/list`
  count 65 confirms no duplicates and no write tool.
- Shipped write count: **0**. `clockify_mcp/writes/` (including the wave-1
  `clockify_tags_create` adapter) is present in the package but is imported by
  no server code path (proved at runtime via `sys.modules`).

## 4. Network / SDK invariants (spot-verified against source + tests)

- Exactly-one credential: `Credential.__init__` raises unless
  `bool(api_key) != bool(addon_token)` (`_transport/auth.py:16`).
- Secret read only at header-attach time, after final-host validation;
  `follow_redirects=False` hard-set in the executor
  (`_transport/executor.py:177`).
- Read retry gated on `not operation.semantics.mutates`
  (`_transport/executor.py:115`) — semantic, not verb-based, so POST reads
  retry and any write never does.
- Mutation attempts through the read path are blocked by two independent
  layers: `ReadOnlyExecutor` (final boundary, `_transport/executor.py:236`)
  and the pre-dispatch mutates check at `:183`; the five workflows additionally
  receive only a `WorkflowReadClient` capability
  (`clockify_mcp/read_capability.py`, remediation F3) with no `raw.call`, no
  executor attribute, and no mutating methods.

## 5. Hand-mutant campaign (disposable worktree, all reverted, worktree removed)

Baseline in the mutant worktree: 420 passed, 1 skipped (see F-B), 6 deselected.

| # | Mutation | Result | Detected? |
|---|---|---|---|
| M1 | `ReadOnlyExecutor` rejection disabled (`if mutates:` → `if False:`) | **6 failed** | YES |
| M2 | Write auto-retry enabled (drop `not mutates` from retryable) | **2 failed** | YES |
| M3 | Nonce reuse allowed (`ConfirmationAlreadyUsed` never raised) | **3 failed** | YES |
| M4 | Dispatch caller-supplied step instead of stored approved step | **0 failed** | **NO → finding F-A** |
| M5 | Principal + workspace binding removed at consume time | **1 failed** | YES |

## 6. Prior findings F1–F5 (previous audit round)

Confirmed remediated at HEAD by commit `6c0d359`: consume-time workspace
binding is present and mutation-detected (M5), the workflow read-boundary
bypass is closed by `WorkflowReadClient`, and the dot-segment path issue has a
regression test in the encode layer. No regression observed.

## 7. Findings

### F-A — MEDIUM — stored-step dispatch defense has no pinning test (mutant M4 survives)

- **Files:** `src/clockify_mcp/writes/executor.py:91-93`,
  `tests/mcp/writes/test_controlled_executor.py`.
- **Proof:** in the disposable worktree, replacing
  `await self._sender(approved_step)` with `await self._sender(step)` (the
  caller's object) leaves the entire non-live suite green (420 passed).
- **Violated invariant:** MCP_WRITE_SAFETY_PLAN — dispatch must use the stored
  approved request bytes; the code comment for "review finding X" states the
  gate must not depend on `request_digest` covering every current and future
  `WriteStep` field, yet only the digest comparison is test-enforced.
- **Real consequence:** none today — `WriteStep.request_digest`
  (`writes/plan.py:48-64`) currently covers every dispatch-relevant field
  (operation, method, service, path template + arguments, query, body sha256,
  multipart fields, file digests), so a digest-equal caller step is
  byte-equivalent. The defense-in-depth for a future non-digested field is
  unprotected by tests and would silently rot.
- **Smallest correct repair:** one test that dispatches with a caller `WriteStep`
  object distinct from the stored one and asserts (via a capturing sender) that
  the sender received the identity object `permit.plan.steps[i]`
  (`assert received is approved_step`).
- **Regression test that must fail first:** exactly that test, run against
  mutant M4.
- **False-positive checks:** confirmed the digest currently covers all fields
  (so this is a test gap, not a live bypass); confirmed the writes package is
  unregistered in the shipped server, so severity stays MEDIUM and blocks only
  write enablement, not the read-only release.

### F-B — LOW — contract surface test silently degrades to SKIP without sibling evidence

- **Files:** `tests/contract/test_complete_surface.py:85`.
- **Proof:** in a Git worktree placed outside `addons-me`, the suite reports
  "SKIPPED … corrected OpenAPI evidence not present" and still exits green
  (420 passed, 1 skipped). A release gate run from any checkout that lacks
  `../clockify-ts-sdk` loses this reconciliation without failing.
- **Violated invariant:** master-plan gate discipline — completeness evidence
  should not silently disappear from a green run.
- **Consequence:** low; the check did run in the canonical checkout during this
  audit and passed, and this report reconciles the counts independently.
- **Smallest repair:** make the skip conditional on an explicit opt-out
  (e.g. env var), or fail when the evidence path is absent and the run is not
  explicitly marked evidence-less.
- **Regression test:** run the suite from a path without the sibling and assert
  non-zero exit unless the opt-out is set.
- **False-positive checks:** verified the test executes (not skipped) in the
  main checkout.

### F-C — LOW (informational) — completion claim references a superseded commit; dangling objects remain locally

- The claim names `972fd5e`; HEAD is `87e1553` with substantive remediation in
  between. Any release notes must reference HEAD.
- 2 unreachable commits + associated trees/blobs exist in the local object
  store (source-only, no secrets — see §1). They are local-only and will age
  out with `git gc`; nothing reachable or pushable contains them. No repair
  required; `git gc --prune=now` optional.

## 8. Maintainability

- No runtime public generation, no `__getattr__` surface, no decorator
  scanning, no import-time registration side effects (verified in
  `tools/__init__.py` and by the `sys.modules` probe).
- Operation truth lives once, in 21 static domain modules aggregated by
  `operations/registry.py`; models are static committed Pydantic v2.
- Adding an ordinary endpoint follows a locatable path: manifest record →
  domain operation module → resource method → focused test; naming makes each
  hop greppable without chat history.
- No generic CRUD framework, no unused abstraction observed; the one
  intentionally dormant subsystem (`writes/`) is clearly bounded and
  documented as unregistered.

## 9. Cleanup attestation

The disposable mutant worktree, both wheel-test venvs, and the stdio probe
script were removed. `git worktree list` shows only the main worktree;
`git status` is clean. No production source, ref, or remote was modified.
This file is the single persistent artifact of the audit.

## 10. Remediation appendix (2026-08-12, same day; release-candidate commit = direct successor of `87e1553`)

Findings F-A and F-B were remediated test-first in one focused commit. F-C is
resolved by referencing that commit (this repository's HEAD after remediation)
as the release candidate in `IMPLEMENTATION_STATUS.md`.

### F-A remediation — identity-pinning regression test

- New test:
  `tests/mcp/writes/test_controlled_executor.py::test_sender_receives_stored_approved_step_by_identity`.
  It builds a consumed permit, dispatches a caller-owned `WriteStep` that is
  equal in every digested field (`==` and `request_digest` equality both
  asserted), captures the object the sender received, and asserts by identity:
  `received_step is permit.plan.steps[0]` and `received_step is not caller_step`.
- **Pre-fix mutant proof:** in a disposable worktree at `87e1553` with its own
  synced environment, the hand mutant
  `await self._sender(approved_step)` → `await self._sender(step)` was applied
  (mutant M4). The new test **failed** exactly on the identity assertion
  (`assert received_step is permit.plan.steps[0]` → `AssertionError`); against
  unmutated production code it passes. Worktree removed
  (`git worktree list` → main only).
- No mutation framework or new abstraction was added.

### F-B remediation — evidence must not silently disappear

- `tests/contract/test_complete_surface.py` no longer uses
  `skipif(not SPEC_PATH.exists())`. A small `evidence_gate()` decides:
  evidence present → the reconciliation **runs**; evidence absent → the test
  **fails** with an actionable message naming the evidence repository URL and
  pinned commit `d7091a44a1b95d4918fa17a7f9b174bf668a9136`; evidence absent
  with `CLOCKIFY_ALLOW_MISSING_TS_SDK_EVIDENCE=1` set explicitly → **one
  clearly explained skip**. `test_evidence_gate_states` pins all three states.
- End-to-end proof (commands run during remediation):
  - present: `uv run pytest -q tests/contract/test_complete_surface.py` →
    10 passed (reconciliation executed).
  - absent, no opt-out: the same test file run from a location whose sibling
    path lacks the evidence repo → **1 failed** with the actionable message.
  - absent, opt-out: same run with `CLOCKIFY_ALLOW_MISSING_TS_SDK_EVIDENCE=1`
    → **1 skipped**, reason explains the explicit opt-out.
- `.github/workflows/ci.yml` now checks out the project and
  `apet97/clockify-ts-sdk` at exactly the pinned commit
  `d7091a44a1b95d4918fa17a7f9b174bf668a9136` as sibling directories; the
  workflow never sets the opt-out variable.

### Final release-proof commands (all green)

- `uv sync --all-extras --dev`; `uv run ruff check .`;
  `uv run ruff format --check .`; `uv run pyright` (0 errors);
  `uv run pytest -q -m "not live"` → **423 passed, 6 deselected**; `uv build`.
- Exact wheel `clockify_python_115-0.1.0-py3-none-any.whl[mcp]` installed into
  clean uv venvs on Python **3.11, 3.13, 3.14**: `ClockifyClient` import and
  `clockify-mcp --help` pass in each.
- Python 3.14: `tests/contract/test_signature_introspection.py` (the PEP 649
  regression contract) run against the **installed** artifact → passed.
- Installed 3.11 artifact spawned over real stdio: **65 tools** (60 raw reads +
  exactly the five workflows `clockify_status`, `clockify_workspace_overview`,
  `clockify_review_day`, `clockify_review_week`, `clockify_doctor`), **zero**
  write-suffixed tools, one controlled read (`clockify_status`) returned live
  workspace/user/running-entry data, stdout protocol-only.
- Sibling `../clockify-ts-sdk` unchanged (clean, HEAD `d7091a4`); all
  worktrees, probe scripts, and smoke venvs removed.

MCP write tools remain **unregistered**; nothing in this remediation claims
public write readiness. External blockers (independent human review of
`clockify_mcp/writes`, two real-host approval-UI proofs) stand.

## 11. Full-repository re-review round 3 (2026-08-12, reviewed commit 232f06a)

Two fresh-context read-only reviewers (SDK/transport/packaging; MCP
boundaries/write-safety) attacked the whole repository with no repair
rationale provided. All BLOCKER/HIGH/MEDIUM candidates were reproduced on the
main thread before any production change; every fix landed test-first (red
proof captured).

Confirmed and repaired:
- **R3-1 HIGH** — multipart list body fields serialized as a Python repr:
  `expenses.update` sent `changeFields` as `"['USER', 'DATE']"` instead of one
  repeated part per item (TS evidence:
  `wrapper/tests/expense-update-multipart.test.ts`). Fix: multipart form is
  now ordered `(key, value)` pairs; lists expand to repeated parts
  (`src/clockify/_transport/encode.py`, executor pass-through). Regression:
  strengthened `test_update_multipart_sends_change_fields` pins part counts
  and exact bare values (also closes R3-3 LOW, the name-only assertion gap
  that let R3-1 ship).
- **R3-2 MEDIUM** — `ExpenseCreateRequest.file` / `ExpenseUpdateRequest.file`
  (`bytes`) were declared but unusable: json-mode dump crashed with
  `UnicodeDecodeError` on real binary; UTF-8-decodable bytes would have become
  a colliding text part. Fix: multipart bodies dump in python mode and bytes
  body fields fail closed pre-network with guidance to use `file=Upload(...)`.
  Regression: `test_bytes_in_model_file_field_rejected_before_http`.
- **R3-4 LOW** — nonce tombstone expired at the *original* permit
  `expires_at`, so replay of a late consume degraded from
  `ConfirmationAlreadyUsed` to `ConfirmationNotFound` (single-use itself never
  broken). Fix: tombstone now lives a full ttl from consumption
  (`nonce_store.py`). Regression:
  `test_replay_after_late_consume_reports_already_used`.
- **R3-5 LOW (docs)** — `read_capability.py` claimed "no executor attribute";
  bound methods expose `__self__._executor` (and `._inner`). Docstring
  corrected to state the reach-through honestly. Severing it was rejected as
  overengineering: the module's stated trust model is capability discipline,
  not a sandbox, and the tripwire tests stand. Reviewer note kept for future
  write waves: preview redaction is builder convention (W-13), not structural
  enforcement — re-check per adapter.

Rejected / no-action:
- Live-suite 401s during baseline were a revoked stale `CLOCKIFY_API_KEY`
  inherited from the operator shell profile shadowing `.env` — environment,
  not product; suite is 6/6 green with zero residue when `.env` is sourced.
- Everything else both reviewers checked (counts 168/29/168/62/106,
  full manifest↔spec parity both directions with 0 mismatches, transport
  invariants, structurally read-only server, permit/nonce/identity-dispatch,
  evidence gate, packaging, secret sweep of full history) was found sound.

Post-repair proof at the release-candidate commit (direct successor of
232f06a): ruff/format/pyright clean; `pytest -m "not live"` → 425 passed;
`pytest -m live` → 6 passed, zero residue; fresh wheel installed into clean
3.11 and 3.14 venvs (import, `clockify-mcp --help`, 3.14 introspection of all
168 methods against the installed artifact); installed-3.11 real-stdio
session: 65 tools = 60 raw + exactly the 5 workflows, zero writes, controlled
read green, protocol-only stdout. Sibling `../clockify-ts-sdk` untouched at
`d7091a4`. No push, publish, or tag.

**Verdict: READ-ONLY RELEASE READY — EXTERNAL WRITE BLOCKERS REMAIN.**
