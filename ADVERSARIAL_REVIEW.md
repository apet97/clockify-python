# ADVERSARIAL_REVIEW.md

Independent release audit of `clockify-python-115` at commit `972fd5e`.
Date: 2026-08-12. Auditor session: adversarial review only; nothing was repaired.
All claims below were re-derived from source, the manifest, and executable evidence —
not from `IMPLEMENTATION_STATUS.md`, commit messages, or the repo's own count tests.

## Verdict

**PASS WITH EXTERNAL WRITE BLOCKERS** — the read-only release mode is ready.
Writes remain disabled pending independent human approval and real-host approval-UI
evidence, **plus the two write-core test gaps below (findings F2, F3), which must be
repaired before any write tool is registered**. No finding affects the shipped
read-only server's behavior against any external input.

## 1. Baseline (independently verified)

- HEAD `972fd5ee7579bd2b1dd2e4e7d5ee7073ba8b9b3a`, working tree clean.
- Blueprint SHA-256:
  - `MASTER_IMPLEMENTATION_PLAN.md` `98cd9d525d6b90d7c0f8fd72df04d4c30a43d1034d00a25d7b050cbe983f9513`
  - `MCP_WRITE_SAFETY_PLAN.md` `f278b1ddbcd846b31e31d54ccd9942b460f13bf0e5fc5e16943d0b6ded200311`
  - `OPERATION_PORT_MANIFEST.md` `c980a24fcf87c91b504a500744e1c8a3cda9b5116a78135769695d45a30e2846`
- Sibling `../clockify-ts-sdk`: HEAD `d7091a44a1b95d4918fa17a7f9b174bf668a9136`, status clean, never modified.
- `pyproject.toml`: distribution `clockify-python-115` 0.1.0; packages `src/clockify` +
  `src/clockify_mcp`; console `clockify-mcp = clockify_mcp.__main__:main`; Python >= 3.11;
  runtime deps httpx + pydantic only; MCP deps behind `[mcp]` extra. Dependency direction
  correct: `clockify` never imports `clockify_mcp`.
- Credential in Git: `.mcp.json` is absent from every reachable commit
  (`git rev-list --all` tree scan: zero hits) and from every ref. `git log -S CLOCKIFY_API_KEY`
  over all refs: zero hits. All 8 dangling objects scanned: no credential content.
  **Separately reported (F1): one reflog-only commit still holds the key — see findings.**
- Wheel (167 files) and sdist (259 files) inspected byte-level: no `.env`, no `.mcp.json`,
  no credential-shaped content, no test files in the wheel.

## 2. Gates (run by the auditor, not replayed from claims)

| Gate | Result |
|---|---|
| `uv sync --all-extras --dev` | OK |
| `uv run ruff check .` | All checks passed |
| `uv run ruff format --check .` | 240 files already formatted |
| `uv run pyright` | 0 errors, 0 warnings |
| `uv run pytest -q -m "not live"` | **407 passed**, 6 deselected |
| `uv build` | wheel + sdist built |
| Fresh venv Python 3.11, `wheel[mcp]` | `ClockifyClient` imports; `clockify-mcp --help` exit 0 |
| Fresh venv Python 3.14, `wheel[mcp]` | `ClockifyClient` imports; `clockify-mcp --help` exit 0 |
| Installed wheel over real stdio | 65 tools listed; all 5 workflows present exactly once; **zero** tools with `read_only_hint=False`; one controlled read (`clockify_status`) succeeded, `is_error=False` |

## 3. Completeness (reconciled from an independent manifest parse)

An auditor-written parser extracted all operation records from
`docs/port/OPERATION_PORT_MANIFEST.md` and compared them to the live registry.

- Manifest: exactly **168** records, no duplicate ids. Registry `ALL_OPERATIONS` /
  `BY_ID` / `BY_PUBLIC_METHOD` = 168 each; set diff empty in both directions;
  per-op method/path/service/mutation/public-method equality: **0 mismatches**.
- Classifications: 62 reads (49 GET + 13 POST reads, each POST-read named and matched to
  a `non-mutating` manifest label), 106 writes; **zero GET-verb writes** exist.
- Exactly 3 multipart operations (`createExpense`, `updateExpense`, `uploadImage`),
  identical set in manifest and runtime `request_encoding`.
- Service routing 157 (regular) / 10 (reports) / 1 (audit log) — matches 157/10/1.
- 29 resources on `ClockifyClient`; exactly 168 public callables; bijection between
  public methods and operations confirmed by introspection (empty diff both ways).
- MCP read server (mock transport): 65 unique tools = 60 raw reads + the 5 named
  workflows (`clockify_status`, `clockify_workspace_overview`, `clockify_review_day`,
  `clockify_review_week`, `clockify_doctor`), each exposed exactly once; every raw tool
  maps to a non-mutating operation. The 62−60 gap is the two binary reads
  (`expenses.download_receipt`, `invoices.export`), excluded by the master plan.
- 8 random end-to-end spot checks (seed 20260812): manifest record → operation constant
  → resource method → focused wiring test — all 8 intact.

## 4. Network / SDK boundary (attacked from source + tests)

Confirmed by direct code inspection and targeted execution:

- Exactly-one-credential XOR enforced (`auth.py:16`); empty strings coerced to absent;
  repr/str redact the secret (verified live: `secret=<redacted>`).
- `validate_destination` runs **before** `Credential.attach`; `follow_redirects=False`;
  custom hosts are explicit opt-in.
- Retry keyed on `operation.semantics.mutates`, not HTTP verb: POST reads retryable,
  writes never (mutant #2 below proves the tests bite); no retry policy by default.
- Transport error on a write → `MutationOutcomeUnknownError`, except provably-undispatched
  `ConnectError`/`ConnectTimeout` → plain transport error. Correct semantics.
- Pagination: empty page, `Last-Page: true`, short-page-without-header, repeated-page
  loop (`PaginationLoopError`), and `max_pages` (`PaginationIncompleteError` with partial
  items) all implemented as specified.
- `raw.call` accepts only registered operation ids and passes through `ReadOnlyExecutor`,
  which rejects `mutates=True` before any HTTP (backend saw zero requests in tests).
- Shared-report view rejects PDF/XLSX before network (`tools/shared_reports.py:48-50`,
  exercised over real stdio).

## 5. Read-server structural proofs

- Fresh interpreter importing `clockify_mcp.server` (source tree **and** installed wheel):
  zero `clockify_mcp.writes*` modules loaded.
- Server construction makes no Clockify request (asserted against a recording backend).
- stdout is protocol-only: all `print()` in `__main__.py` go to stderr; logging is
  configured to stderr; the failure path proves `stdout == b""`.
- No `__getattr__`, no runtime generation, no decorator scanning, no TODO/pass/
  NotImplementedError in production paths (the only `pass` bodies are exception classes
  in the never-imported `writes/` package). Single operation truth: `registry.BY_ID`.

## 6. Write-safety core: direct attacks (all blocked)

Auditor-written attack script against `WriteGate`/`InMemoryNonceStore` (no repo tests used):

| Attack | Result |
|---|---|
| Replay consume after consumption | blocked (`ConfirmationAlreadyUsed`) |
| Tampered plan digest between preview and consume | blocked (`ConfirmationMismatch`) |
| Wrong principal consuming a valid nonce | blocked (`ConfirmationMismatch`) |
| 100 concurrent consumers on one nonce | exactly **1** permit issued |
| Changed arguments digest after prepare | blocked (`ConfirmationMismatch`) |

Existing suite additionally covers expiry, wrong audience/process key, state drift,
step-order/extra-step violations, cancellation at every boundary, 4xx/5xx/transport
ambiguity without retry, preview exact-wire visibility, and nonce memory/TTL/entry bounds
(70 write tests) — and the mutants below prove most of those tests actually bite.

## 7. Hand-mutant experiments (disposable worktree, removed after use)

Baseline in the worktree: 361 relevant tests green before mutating. Each mutant was a
minimal hand edit, reverted between runs.

| # | Mutant | Detected? |
|---|---|---|
| 1 | `ReadOnlyExecutor` mutates-rejection neutralized | **YES** — 5 tests fail |
| 2 | Write auto-retry enabled in `HttpExecutor` | **YES** — 2 tests fail |
| 3 | Nonce reuse allowed (`consume` keeps the pending record) | **YES** — 5 tests fail |
| 4 | Caller-supplied step dispatched + digest check removed | **YES** — 2 tests fail |
| 5a | Principal binding dropped from `consume()` | **YES** — 2 tests fail |
| 5b | `workspace_id` dropped from `derive_key` HMAC material | **NO — full suite passes** → finding F2 |
| 6 | `TAGS_CREATE` classification flipped to non-mutating | **YES** — 11 tests fail |
| 7 | Workflow unwraps `client._executor._inner` and mutates | **NO — workflow tests pass** → finding F3 |

Worktree removed and pruned; main worktree verified untouched and clean afterward.

## 8. Findings

### F1 — MEDIUM · live API key survives in a reflog-only commit
- **Files:** local Git metadata only (`.git/logs`, unreachable commit `63dd88c`); not in any ref or reachable commit.
- **Proof:** `for c in $(git rev-list --reflog); do git ls-tree -r --name-only $c | grep -q '^\.mcp\.json$' && echo $c; done` → `63dd88c…`; its `.mcp.json` holds the same live key as the current untracked file (compared without printing).
- **Invariant violated:** "no credential in Git history" — holds for reachable history, not for local reflog.
- **Consequence:** local-only. `git clone`/`git push` never transfer reflogs, so the key cannot leave this machine through normal Git operations; a wholesale copy of the `.git` directory would carry it.
- **Smallest repair:** `git reflog expire --expire-unreachable=now --all && git gc --prune=now`, then rotate the sacrificial key.
- **Regression check:** re-run the reflog scan above; must print nothing.
- **False-positive rejection:** verified the commit is in no branch/ref (`git branch --contains` empty) and absent from `rev-list --all`; verified the blob really contains the credential key name and the live value.

### F2 — MEDIUM (write-ship blocker) · workspace binding in `derive_key` has zero test coverage
- **Files:** `src/clockify_mcp/writes/principal.py` (`derive_key`), tests missing.
- **Proof:** mutant 5b — removing `workspace_id` from the HMAC key material passes the entire non-live suite (406 passed, 1 skipped).
- **Invariant violated:** MCP_WRITE_SAFETY_PLAN requires the pending confirmation to be bound to the workspace; the required mutant-detection item "omission of principal/**workspace** binding" is only half-detected (principal yes, workspace no).
- **Consequence:** a future refactor could silently drop workspace binding; two preparations differing only by workspace could collide on the pending key. Partial defense remains (`get_or_issue` reuse compares `existing.workspace_id`), and `consume()` never checks workspace — key derivation is the intended barrier. Not exploitable in the shipped read-only release (writes unregistered).
- **Smallest repair:** unit test asserting `derive_key(..., workspace_id="w1") != derive_key(..., workspace_id="w2")` (all else equal), plus a gate-level test that two same-argument prepares in different workspaces yield distinct nonces.
- **Regression test:** the new tests must fail under mutant 5b.
- **False-positive rejection:** full-suite run under the mutant, not a subset; grep confirmed no existing test references `derive_key`.

### F3 — MEDIUM (write-ship blocker) · workflow code can route around `ReadOnlyExecutor` via `client._executor._inner`, undetected by tests
- **Files:** `src/clockify_mcp/workflows/*` (capability), `src/clockify/client.py` (`_executor` exposure), `tests/mcp/test_workflows.py` (missing tripwire).
- **Proof:** mutant 7 — a workflow edited to call `client._executor._inner.execute(TAGS_CREATE, ...)` issued a real `POST /workspaces/w-test/tags` against the recording backend while all 8 workflow tests passed.
- **Invariant violated:** the safety plan's requirement that a workflow sub-call bypass be caught by tests before any mutation reaches the transport.
- **Consequence:** internal-only — exploiting it requires editing repository source; no external input can reach the inner executor. The public boundary holds (`test_workflows_cannot_mutate` passes on unmutated code). It is a tripwire gap, not a runtime hole in the shipped server.
- **Smallest repair:** a workflow-level invariant test that runs every workflow against a recording backend and asserts zero mutating-verb requests; optionally stop handing workflows a client whose private `_executor` wraps a write-capable inner executor.
- **Regression test:** the new invariant test must fail under mutant 7.
- **False-positive rejection:** confirmed the mutated call actually reached MockTransport (request recorded) before concluding the tests missed it.

### F4 — LOW · `"."`/`".."` path arguments survive `render_path` (same-service endpoint retargeting)
- **Files:** `src/clockify/_transport/encode.py:50` (path quoting; non-empty check at :44-47).
- **Proof:** `uv run python -c "from clockify._transport.encode import render_path; from clockify.operations.registry import BY_ID; print(render_path(BY_ID['getWorkspacesWorkspaceIdTags'], {'workspaceId': '..'}))"` → `/workspaces/../tags`; httpx normalizes dot segments, so the request targets a different path on the same service, which still passes `validate_destination`.
- **Invariant violated:** compiled requests must target exactly the operation's declared endpoint.
- **Consequence:** bounded — `/` is percent-encoded so only the literals `"."`/`".."` escape; same host only; in the MCP only reads are reachable. A model-supplied id of `".."` could silently hit a different read endpoint; direct SDK use could retarget within the service.
- **Smallest repair:** reject path-arg values equal to `"."` or `".."` next to the existing non-empty check; one unit test.
- **Regression test:** `render_path(op, {"workspaceId": ".."})` must raise; fails before the repair.
- **False-positive rejection:** verified `quote(value, safe="")` does encode `/` (`"a/b"` → `a%2Fb`), so full traversal strings are already blocked; only the two dot literals escape.

### F5 — LOW · Python 3.14 `inspect.signature()` fails on 12 resource methods (PEP 649 + builtin shadowing)
- **Files:** e.g. `src/clockify/resources/invoice_payments.py:57`; 12 methods across approvals, clients, invoice_payments, invoices, projects, tags, tasks, time_off_policies, user_groups, users (`filter`, `grant_manager_role`), workspaces.
- **Proof:** under a 3.14 interpreter, `inspect.signature(client.tags.list)` raises `TypeError: 'function' object is not subscriptable` — deferred annotation `-> list[TagDto]` evaluates in class scope where a sibling method named `list` shadows the builtin.
- **Invariant violated:** none of the plan's hard invariants; runtime annotation introspection only. Calls, pyright, and MCP tool schemas (standalone functions) are unaffected — the 3.14 wheel smoke and full suite pass.
- **Consequence:** third-party tooling doing runtime introspection on 3.14 breaks on those 12 bound methods.
- **Smallest repair:** quote the affected return annotations (or module-level `ListOfX` aliases as already used elsewhere in the repo).
- **Regression test:** a unit test calling `inspect.signature` on all 168 public methods; fails on 3.14 before the repair.
- **False-positive rejection:** reproduced on the project's own 3.14 venv; confirmed normal invocation of the same methods works.

No BLOCKER and no HIGH-severity runtime defect was found. All other attacked
surfaces — listed in sections 3–7 — were confirmed intact with executable evidence.

## 9. Cleanup

Disposable mutant worktree removed and pruned (`git worktree list` shows only the main
worktree, clean at `972fd5e`). Temporary venvs/probe scripts lived in the session
scratchpad and `/tmp` scratch files were deleted. No production source, no Git ref, and
no sibling-repository file was modified by this audit. This file is the audit's only
persistent artifact.

---

## Appendix: remediation wave (2026-08-12, same day)

All five findings were re-reproduced before any code change, then repaired
test-first. Suite grew 407 → 421 (all green); every gate re-run; wheel
re-verified on clean Python 3.11 and 3.14 with real-stdio proof (65 tools,
5 workflows, zero write-hinted tools, controlled `clockify_status` read
`is_error=False`); live suite 6/6 with an independent zero-residue sweep
(0 `py115*` tags, 0 projects). Public MCP write registration remains zero; the
wave-1 tag-write adapter stays unregistered.

### F1 — CONFIRMED (local-only) · owner actions recorded
- **Reproduced:** reflog-only commit `63dd88c` still holds `.mcp.json`.
  Re-verified: zero tracked files, zero reachable commits (`rev-list --all`
  tree scan), zero refs, wheel and sdist byte-listed clean.
- **Fix:** none in-repo (Git metadata is not repository content, and destructive
  `reflog expire`/`gc` was not run against a tree with active uncommitted work).
- **Owner actions (required, not automatable here):**
  1. `git reflog expire --expire-unreachable=now --all && git gc --prune=now`
     on a clean tree; re-run the reflog scan (must print nothing).
  2. Rotate the sacrificial `CLOCKIFY_API_KEY` in the Clockify UI.
- **Proof of scope:** the key cannot leave the machine via clone/push; only a
  wholesale `.git` copy carries it.

### F2 — CONFIRMED (test gap + one real hole) · repaired
- **Reproduced:** no test referenced `derive_key`; mutant 5b (workspace_id
  dropped from the HMAC material) passed the full suite. Additionally
  confirmed the review's note that `consume()` never verified workspace.
- **Test first:** `tests/mcp/writes/test_workspace_binding.py` — key
  derivation (`derive_key` differs by workspace only), stored-record lookup
  (two same-argument prepares in workspaces A/B yield distinct keys+nonces,
  independently consumable; same-workspace reuse still returns one nonce),
  and consume-time verification (tampered `workspace_id` on a valid
  `PreparedWrite` must raise `ConfirmationMismatch`).
- **Red proof:** consume-time test failed on pre-fix code (`DID NOT RAISE`);
  in a disposable worktree under mutant 5b, the derivation and prepare tests
  failed (2 failed). Worktree removed and pruned.
- **Fix:** `InMemoryNonceStore.consume` now takes `workspace_id` and checks it
  against the stored record alongside principal/tool/arguments/plan digests;
  `WriteGate.consume` passes `prepared.workspace_id`.

### F3 — CONFIRMED · repaired
- **Fix:** new `clockify_mcp/read_capability.py` — `WorkflowReadClient`, a
  slotted façade exposing exactly the reads the five workflows use
  (users.me/list, workspaces.get, time_entries.list_in_progress/list_for_user,
  projects.list/get, tags.list, reports.weekly, `workspace_id`). All five
  workflow implementations now accept it; `register_workflows` builds it once
  and never hands workflows the `ClockifyClient`. No `raw`, no `_executor`,
  no general dispatch on its ordinary API. `ReadOnlyExecutor` remains the
  final runtime boundary; this is capability discipline plus a tripwire, not
  a claim that Python resists malicious source edits.
- **Tests:** `tests/mcp/test_workflow_capability.py` — (1) a spy proves the
  registered tools pass a `WorkflowReadClient`, not a `ClockifyClient`;
  (2) surface assertions (slots-only, no raw/executor/mutators anywhere);
  (3) a mutation reaching `ReadOnlyExecutor` raises
  `ClockifyReadOnlyViolation` with zero HTTP dispatched; (4) an invariant
  tripwire runs all five workflows end-to-end and asserts every dispatched
  request is a read (GET or the POST weekly report). Existing 8 workflow
  behavior tests unchanged and green.
- **Mutant proof:** in a disposable worktree, mutant 7 re-attempted through
  the new façade (`client.tags.list.__self__._executor._inner` → new
  `TagsResource` → live POST). The tripwire test fails (1 failed). Worktree
  removed and pruned.

### F4 — CONFIRMED · repaired
- **Reproduced:** `render_path(op, {"workspaceId": ".."})` →
  `/workspaces/../tags` (and `"."` likewise).
- **Test first:** `tests/unit/transport/test_encode_paths.py` — `"."` and
  `".."` rejected; a normal id renders; embedded slash stays percent-encoded
  (`a/b` → `a%2Fb`, `../x` → `..%2Fx`); pre-encoded `%2e%2e` is re-quoted to
  inert data; `"..."` remains a valid opaque id. Red: 2 failures pre-fix.
- **Fix:** `render_path` rejects a complete path argument equal to `"."` or
  `".."` with `ClockifyConfigurationError`, next to the existing non-empty
  check — before URL construction, before HTTP. No policy framework added.

### F5 — CONFIRMED · repaired
- **Reproduced:** on Python 3.14, `inspect.signature()` raised
  `TypeError: 'function' object is not subscriptable` on exactly the 12
  reported methods (PEP 649 deferred annotations evaluating in class scope
  where a sibling `list`/`filter` method shadows the builtin).
- **Fix:** the affected signatures now use explicit `builtins.list[...]`
  (with `import builtins`) in the 11 resource modules; nothing catches or
  suppresses introspection errors.
- **Contract test:** `tests/contract/test_signature_introspection.py`
  introspects every public coroutine method across all 29 resource classes
  and asserts the introspected set equals `BY_PUBLIC_METHOD` with exactly
  168 methods. Run green on Python 3.11 (project venv) and Python 3.14
  (clean venv against the source install; wheel separately smoke-verified).

### Re-verification after the wave
`uv sync --all-extras --dev`, `ruff check`, `ruff format --check` (246 files),
`pyright` (0 errors), `pytest -q -m "not live"` (421 passed), `uv build`;
clean-venv `wheel[mcp]` installs on 3.11 and 3.14 (`ClockifyClient` imports,
`clockify-mcp --help` exit 0); installed executable over real stdio: 65 tools,
5 workflows exactly once, zero `read_only_hint=False`, controlled read OK;
live suite 6 passed, zero residue. Write readiness is NOT claimed: independent
human review of `clockify_mcp/writes` and approval-UI evidence in two intended
hosts remain external blockers.
