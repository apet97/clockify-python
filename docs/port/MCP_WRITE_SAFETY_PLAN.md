# Clockify Python MCP Write Safety Plan

**Status:** focused design milestone. This plan does not authorize any MCP mutation to ship.

**Scope:** agent-facing Clockify writes only. Normal Python SDK writes remain direct and do not use this confirmation system.

## Source-grounded protocol findings

| Finding | Status | Consequence |
|---|---|---|
| MCP `2026-07-28` replaces server-initiated interaction with Multi Round-Trip Requests. A server returns `InputRequiredResult`; the client retries the same call with `inputResponses` and echoed `requestState`. | FACT | Confirmation can be part of the original tool call without exposing a model-supplied token argument. |
| Official Python SDK v2’s `Resolve(Elicit(...))` dependency uses MRTR on modern protocol and the supported synchronous elicitation path on legacy protocol. | FACT | Use one high-level confirmation dependency rather than maintaining separate product tool bodies by protocol era. |
| A resolved parameter is omitted from the model-visible tool schema and cannot be supplied by tool arguments. | FACT | Approval is a server/client contract, not a `confirm=true` value the model can invent. |
| `MCPServer` seals outgoing request state and verifies inbound state. Its boundary binds expiry, method, tool/resource target, argument digest, audience, and an authenticated principal when one exists. | FACT | Do not implement custom request-state cryptography. Configure the official boundary correctly. |
| Default request-state protection is process-local and is suitable for stdio or one HTTP worker. | FACT | The initial product uses one process-local key and one process-local nonce store. |
| The official request-state boundary does not maintain an atomic consumed-nonce/JTI set. A valid state can be echoed again within its lifetime. | FACT from official source inspection | Request-state integrity is necessary but not sufficient for true single-use execution. |
| Resolver bodies can run again on every MRTR round. The SDK reuses a recorded answer only when the exact rendered question is unchanged. | FACT | Preview rendering must be deterministic; volatile values must be stored and reused, not regenerated into a different question. |
| A manual `InputRequiredResult` on a pre-2026 session produces an invalid-result protocol error unless the server branches by protocol. | FACT | Use `Resolve(Elicit(...))` for the normal tool path; reserve manual MRTR for low-level tests or a proven exceptional need. |
| Tool annotations are hints and are not enforcement. | FACT | No safety property depends on `destructiveHint`, `idempotentHint`, or `readOnlyHint`. |

## Design decision

The write path uses:

```text
validated tool arguments
        │
        ▼
read-only plan builder
        │
        ▼
server-side PreparedWrite + stable nonce
        │
        ▼
Resolve(Elicit(exact deterministic preview))
        │
        ├── modern client → MRTR + sealed requestState
        └── legacy client → synchronous elicitation
        │
        ▼
atomic nonce consumption
        │
        ▼
exact ordered ExecutionPermit
        │
        ▼
ControlledWriteExecutor
        │
        ▼
Clockify
```

This is smaller and stronger than translating the TypeScript `dry_run`/`confirm_token` store:

- approval is invisible to the model;
- modern and legacy protocol behavior comes from the official SDK;
- the official request-state boundary provides integrity and request/principal binding;
- the server stores the exact plan and provides atomic one-time use;
- the final executor is bound to approved wire semantics, not merely to a tool name.

## Trust model

### Trusted for the initial stdio product

- local server process and installed package code;
- server configuration supplied by the operator;
- the official MCP Python SDK’s request-state implementation;
- the target MCP host only after compatibility testing proves that it presents elicitation to the user and does not silently auto-accept;
- Clockify TLS and the fixed Clockify service hosts after destination validation.

### Untrusted input

- model-generated tool arguments;
- every client-supplied header not produced by authenticated middleware;
- `inputResponses`, except as the host’s representation of a user decision;
- echoed `requestState` until the SDK verifies it;
- Clockify response content, including names/descriptions that can contain untrusted text;
- external webhook URLs and file metadata;
- timing, retries, cancellation, and duplicated/concurrent requests.

### What the server can prove

The server can prove that:

- the approved preview corresponds to the same tool and exact validated arguments;
- the plan is bound to the configured principal and workspace;
- the confirmation has not expired;
- the server issued the nonce;
- only one execution can consume that nonce;
- the controlled executor receives exactly the approved ordered operation plan;
- no automatic retry occurs after mutation dispatch.

### What the server cannot prove by itself

The server cannot cryptographically prove that a human, rather than a client or automation, saw and approved the elicitation. That assurance belongs to the MCP host UI and is a release requirement. A client that auto-accepts every elicitation is incompatible with safe writes even if protocol tests pass.

The server also cannot eliminate the final race between a precondition read and a Clockify write when Clockify offers no conditional-write token or ETag. It can detect drift before dispatch and explain the residual race; it cannot invent atomic server support.

## Non-goals

This plan does not build:

- a general enterprise authorization platform;
- durable jobs, queues, or background execution;
- cross-device approval;
- multi-region or multi-worker confirmation state;
- a database or Redis for local stdio;
- automatic compensation/rollback;
- write retry based on HTTP verb or a claimed idempotency key;
- autonomous approval based on a `LOW` label;
- proof that a model is resistant to prompt injection.

## Safety invariants

### W-01 — No hidden write exposure

An SDK write operation is not an MCP write tool until an explicit tool function, policy record, preview builder, and test set are reviewed.

### W-02 — Approval is model-invisible

The tool’s approval parameter is resolved through `Annotated[..., Resolve(...)]`. It is absent from the advertised input schema. Tool arguments containing an approval-like field are ignored or rejected by the normal schema.

### W-03 — Preview before mutation

Plan construction may perform reads and local validation only. The read client used by plan builders is backed by `ReadOnlyExecutor`. No HTTP mutation may occur before approval and nonce consumption.

### W-04 — Exact operation binding

A pending confirmation binds the exact ordered operation IDs. A permit for `projects.update` cannot execute `projects.delete`, an extra lifecycle step, or a different endpoint.

### W-05 — Exact argument and wire-plan binding

The pending record binds:

- validated model-visible arguments, preserving omitted versus explicit null;
- resolved workspace and principal;
- path arguments;
- ordered query pairs;
- exact JSON wire body after aliases and operation-specific transformations;
- multipart fields and file hashes when file writes are eventually enabled;
- current-state/precondition fingerprint;
- ordered lifecycle steps.

Any mismatch is rejected before mutation dispatch.

### W-06 — Exact principal binding

A pending record and request state are bound to the configured Clockify credential identity. A confirmation created under one credential cannot execute under another.

### W-07 — Expiry

A confirmation expires after five minutes by default. Expiry is checked by both the official request-state boundary and the nonce store. A new preview is required after expiry.

### W-08 — True single-use

Nonce consumption is atomic and occurs before the first mutation request. The same nonce can never authorize a second dispatch, even under concurrent retries.

### W-09 — No mutation retry

No Clockify mutation is automatically retried. A timeout or connection loss after dispatch is an unknown outcome, not a reason to replay.

### W-10 — State-drift handling

If current Clockify state used by the preview changes before execution, the old approval is not used. During MRTR, a changed deterministic preview causes a new question. Immediately before dispatch, a final precondition mismatch fails the call and requires a new preview.

### W-11 — Ordered multi-step execution

A lifecycle permit contains an ordered list of exact steps. The controlled executor permits only the next step. It cannot skip, repeat, reorder, or add a step.

### W-12 — Partial failure is explicit

If one step succeeds and a later step fails, the result reports the applied steps, failed step, remaining steps, and reconciliation action. The server does not report all-or-nothing success and does not silently rollback.

### W-13 — Secrets do not enter previews or logs

API keys, add-on tokens, webhook auth tokens, and raw file contents are never rendered. Sensitive values may be represented by purpose, length, and a server-side digest only.

### W-14 — Read-only mode remains independently safe

When writes are disabled or the client cannot elicit, all read tools continue to work through `ReadOnlyExecutor`. No fallback converts a failed confirmation into an unguarded write.

### W-15 — Host validation remains below the gate

An approved plan cannot redirect credentials to another host. The same final-host validation and no-redirect rule used by the SDK applies after approval.

### W-16 — Identical concurrent confirmations do not double-submit

Concurrent calls from the same principal with the same tool and exact arguments may share one pending preview while it is outstanding. At most one consumes its nonce. A later call must obtain a fresh nonce and a fresh user approval.

## Components and responsibilities

```text
clockify_mcp/writes/
├── state.py        # enums and result states only
├── plan.py         # WritePlan, WriteStep, deterministic preview
├── principal.py    # credential/OAuth principal binding
├── nonce_store.py  # bounded issue/reuse/invalidate/consume/cancel
├── gate.py         # resolver graph and approval handling
├── executor.py     # exact ordered permit enforcement
└── reconcile.py    # operation-specific read-back helpers
```

No module may both issue an approval and send HTTP. The split is deliberate:

- plan builders know business semantics but have a read-only client;
- the nonce store knows state transitions but not Clockify;
- the gate converts a valid user decision into one consumed permit;
- the controlled executor knows exact requests but not UI;
- reconcilers read after a dispatch and never repeat it.

## Data contracts

### Canonical JSON

Use one canonical encoder for arguments, wire bodies, plan hashes, and preconditions:

- UTF-8 JSON;
- object keys sorted by Unicode code point;
- no insignificant whitespace;
- arrays preserve order;
- explicit null is preserved;
- omitted fields are absent;
- `NaN`, positive infinity, and negative infinity are rejected;
- date/time values are serialized exactly as the request model sends them;
- bytes are represented only by SHA-256, length, filename, and content type.

Do not use Python `repr`, insertion-order-dependent dictionaries, or floating-point string formats that vary by platform.

### Prepared write

```python
@dataclass(frozen=True, slots=True)
class PreparedWrite:
    key: str
    nonce: str
    principal_id: str
    tool_name: str
    workspace_id: str | None
    arguments_digest: str
    plan: WritePlan
    plan_digest: str
    issued_at: float
    expires_at: float
```

`key` is an HMAC over principal, tool name, and canonical validated tool arguments. It supports stable reuse across MRTR rounds without revealing a secret.

`nonce` is 256 bits from `secrets.token_urlsafe(32)` or equivalent. It is included in the deterministic preview as a confirmation ID and stored server-side.

### Write plan

```python
@dataclass(frozen=True, slots=True)
class WritePlan:
    version: int
    title: str
    summary: str
    effect: str
    scope: str
    sensitivity: tuple[str, ...]
    reversibility: str
    steps: tuple[WriteStep, ...]
    preconditions: tuple[Precondition, ...]
    preview_fields: tuple[PreviewField, ...]
    warnings: tuple[str, ...]
    reconciliation: ReconciliationPlan | None
```

```python
@dataclass(frozen=True, slots=True)
class WriteStep:
    operation_id: str
    path_arguments: tuple[tuple[str, str], ...]
    query: tuple[tuple[str, str], ...]
    body_json: bytes | None
    multipart_fields: tuple[tuple[str, str], ...]
    files: tuple[FileDigest, ...]
    request_digest: str
```

The plan stores canonical request components without authentication headers. The real executor attaches credentials only after host validation.

### Approval schema

```python
class WriteApproval(BaseModel):
    decision: Literal["approve", "reject"]
```

The tool consumes the full `ElicitationResult[WriteApproval]` so it can distinguish:

- accepted and approved;
- accepted but rejected;
- client-declined;
- client-cancelled.

Every non-approved outcome cancels or leaves the pending record to expire and performs no mutation.

### Execution permit

```python
@dataclass(frozen=True, slots=True)
class ExecutionPermit:
    permit_id: str
    principal_id: str
    tool_name: str
    arguments_digest: str
    plan: WritePlan
    consumed_at: float
```

Only `WriteGate.consume()` constructs a permit. The controlled executor tracks the next allowed step and invalidates the permit after the final step or any terminal failure.

Python cannot make a constructor cryptographically unforgeable inside the same compromised process. The boundary is for correct product code and adversarial client input, not malicious code already executing in the server process.

## Principal binding

### Initial stdio binding

There is no authenticated MCP principal on ordinary local stdio. Build a stable process-local principal ID from the configured Clockify credential without storing or exposing the credential:

```text
principal_id = HMAC-SHA256(
    process_secret,
    "clockify-principal-v1" || auth_scheme || credential_bytes
)
```

The default workspace is **not** the principal; it is bound separately in arguments/plan state so one credential can safely operate multiple workspaces.

Configure the official request-state security boundary with the same process secret and a custom binder that returns `principal_id`:

```python
RequestStateSecurity(
    keys=[process_secret],
    ttl=300.0,
    bind_principal=lambda _ctx: principal_id,
    audience="clockify-python-mcp",
)
```

The process secret is generated at startup and never persisted. A restart invalidates both pending confirmations and request state, which is the safe stdio behavior.

### Future remote binding

A remote authenticated server should bind request state to the official authenticated OAuth principal and bind the pending record to the same identity plus the selected Clockify credential/account. It must not trust arbitrary headers.

A multi-worker deployment requires **both**:

1. shared request-state keys; and
2. a shared atomic nonce store.

Sharing only the keys would allow the same valid confirmation to reach two independent process-local stores. Do not enable shared keys without replacing the store with a proven atomic backend.

## Nonce store

### Scope and bounds

The initial `InMemoryNonceStore` uses:

- one `asyncio.Lock` for atomic transitions;
- monotonic time for expiry decisions;
- five-minute default TTL;
- maximum 128 pending records;
- maximum 256 KiB canonical plan size per record;
- expiry pruning before capacity checks;
- no persistence.

These limits prevent unbounded memory growth without creating infrastructure. They are configurable at server construction and tested at exact boundaries.

### Record transitions

```text
missing
  │ issue
  ▼
pending ── reject/cancel ──► cancelled
  │
  ├── expires ──────────────► expired
  │
  └── atomic consume ───────► consumed ──► removed + nonce tombstone until expiry
```

A short-lived consumed-nonce tombstone gives a precise replay error. It stores only nonce, principal ID, and expiry, not the request body.

### Stable issue behavior across MRTR rounds

`get_or_issue(key, current_plan)` is atomic:

1. prune expired records/tombstones;
2. if a pending record exists for `key` and its `plan_digest` matches, return it unchanged;
3. if a pending record exists for `key` but current state produces a different plan digest, cancel it and issue a new nonce;
4. if no pending record exists, issue a new nonce and record;
5. if capacity is exhausted after pruning, fail closed before elicitation.

This is why a random nonce can appear in the preview without making the question volatile: the same logical pending call reuses the same stored nonce on every resolver round.

### Atomic consume

`consume(nonce, principal_id, tool_name, arguments_digest, plan_digest)` executes under the lock:

- reject missing, expired, cancelled, or already-consumed nonce;
- compare every binding in constant-time where appropriate;
- remove the pending plan and add a tombstone before returning the permit;
- never restore the nonce after a later failure.

The mutation has not happened yet, but consuming first prevents two callers from dispatching. A failure before dispatch requires a new preview and confirmation.

## Resolver graph and protocol flow

### Tool shape

The intended high-level shape is:

```python
async def prepare_write(
    # same validated tool arguments by name
    ctx: Context,
    ...,
) -> PreparedWrite:
    # read-only client only
    current_plan = await build_exact_plan(...)
    return await nonce_store.get_or_issue(..., current_plan)


def ask_for_approval(
    prepared: Annotated[PreparedWrite, Resolve(prepare_write)],
) -> Elicit[WriteApproval]:
    return Elicit(render_preview(prepared), WriteApproval)


@mcp.tool(...)
async def clockify_projects_delete(
    project_id: str,
    workspace_id: str | None = None,
    prepared: Annotated[PreparedWrite, Resolve(prepare_write)],
    approval: Annotated[
        ElicitationResult[WriteApproval],
        Resolve(ask_for_approval),
    ],
) -> WriteResult:
    if not is_approved(approval):
        await nonce_store.cancel(prepared.nonce)
        return rejected_result(...)

    permit = await write_gate.consume(prepared)
    return await execute_and_reconcile(permit)
```

Exact import names and generic syntax must be verified in Phase 0 against the pinned SDK. The contract above is fixed even if a minor API spelling differs.

### First modern round

1. MCP validates model-visible tool arguments.
2. `prepare_write` resolves IDs, reads current state through `ReadOnlyExecutor`, constructs the exact plan, and gets a stable nonce.
3. `ask_for_approval` renders the deterministic preview.
4. The SDK returns `InputRequiredResult` with an elicitation request and sealed request state.
5. No mutation has occurred.

### Modern retry

1. The client retries the same tool and arguments with response and request state.
2. The official boundary verifies seal, expiry, audience, method, tool name, argument digest, and principal.
3. Resolvers run again. `prepare_write` rebuilds current state.
4. If the plan is unchanged, the nonce and question are unchanged, so the recorded answer is reused.
5. If the plan changed, the old pending record is invalidated and a new question is shown.
6. The tool body receives the current `PreparedWrite` and the elicitation outcome.
7. Only approval causes atomic consumption and execution.

### Legacy call

The same resolver asks through the legacy synchronous elicitation request. The tool body continues only after the result. The nonce store still provides exact binding, expiry, and single-use; request state is not involved in that era.

### Unsupported elicitation

If the target client has no elicitation support or the operator disabled writes:

- write tools either remain unadvertised or fail with a stable `write_confirmation_not_supported` error;
- no fallback approval argument is exposed;
- read tools continue normally.

## Deterministic preview contract

The preview is generated from `WritePlan`, not hand-written independently in each tool. It is stable across rounds for the same pending plan.

Required fields:

```text
Action: Delete project
Confirmation ID: <stable nonce display>
Workspace: <id and safe name when known>
Target: <entity type, id, safe name>
Effect: delete
Steps:
  1. Update project archived=true
  2. Delete project
Current state: active
Result if complete: project removed
Reversibility: archive is reversible; final delete is not
Approved request fields: <exact redacted diff/body>
Warnings: <replacement, financial, membership, bulk, external effects>
Valid for: 5 minutes
Decision: approve or reject
```

Rules:

- show IDs and human-readable names together where safe;
- show exact counts and IDs for bulk operations, with bounded samples only in prose and the complete set in structured preview data;
- show current and proposed values for replace/patch/transition operations;
- show money with the exact wire unit and a human interpretation when possible;
- show every lifecycle step in order;
- show fields omitted from a full replacement when omission has meaning;
- redact secrets while binding their exact value server-side;
- do not include current time, random values other than the stored nonce, or live values not stored in the pending plan;
- produce both human text and structured preview data so client UI tests can inspect exact content.

## Exact binding and request compilation

The Clockify transport should expose a pure request compiler:

```text
(operation, path args, query args, request model, files)
        │
        ▼
CanonicalPreparedRequest
```

It performs the same aliases, query serialization, multipart field conversion, and operation-specific transformations used by normal SDK execution, but does not attach credentials or send HTTP.

The plan stores the compiler result. At execution, `ControlledWriteExecutor` recompiles from the stored structured step, compares `request_digest`, then dispatches. It does not trust a second body constructed by tool code after approval.

Authentication headers and request IDs are excluded from the approved digest because they are transport metadata. Destination service, method, path, query, content type, body, and file digests are included.

## State-change and precondition handling

### Precondition fingerprints

For a mutation whose preview depends on current state, store a canonical fingerprint of the minimum relevant fields, not an entire noisy response. Examples:

- replacing client update: name, archived, address, note, CC emails, and every field sent back;
- tag update: name and archived;
- project update/delete: archived/public/billable and fields used to construct the replacement;
- membership change: current member IDs/roles;
- invoice/payment operation: status, totals, payment IDs, and relevant monetary fields;
- time-off request transition/delete: current status and policy/request identity.

Immediately before first dispatch, read those fields again and compare.

### Outcomes

- **same fingerprint:** continue;
- **changed fingerprint before final approval round:** rendered preview changes and the client is asked again;
- **changed fingerprint after approval but before dispatch:** fail `state_changed_after_approval`; consume the nonce; require a new call;
- **no read route exists:** preview states that no precondition read is possible; use exact arguments and post-write reconciliation only;
- **Clockify offers no conditional write:** document the residual race between final read and dispatch.

Do not “merge” changed state automatically after approval. That would execute an unapproved plan.

## Execution state machine

```text
NEW
 │
 ▼
PREPARING ── validation/read failure ──► FAILED_BEFORE_APPROVAL
 │
 ▼
AWAITING_INPUT ── reject/decline/cancel ──► REJECTED
 │
 ├── expiry ─────────────────────────────► EXPIRED
 │
 ▼
APPROVED
 │ atomic consume
 ▼
CONSUMED
 │ precondition mismatch/cancel
 ├───────────────────────────────────────► FAILED_BEFORE_DISPATCH
 │
 ▼
DISPATCHING_STEP_N
 │
 ├── definitive HTTP failure before any applied step ─► FAILED
 ├── transport/cancel ambiguity ──────────────────────► OUTCOME_UNKNOWN
 ├── later-step failure after applied step(s) ────────► PARTIAL_FAILURE
 └── all steps applied ───────────────────────────────► SUCCEEDED
                                                        │
                                                        ├── read-back ok → RECONCILED
                                                        └── read-back fails → SUCCEEDED_UNRECONCILED
```

A state is reported, not inferred by the caller from prose.

## Controlled executor

`ControlledWriteExecutor` accepts only an `ExecutionPermit` and the next plan step.

Before every dispatch it checks:

- permit not terminal;
- principal and tool match;
- step index is the next index;
- operation ID matches;
- compiled method/service/path/query/body/file digest matches;
- operation is mutating;
- destination host is valid.

After dispatch:

- record success and advance one step;
- on definitive HTTP error, mark terminal;
- on transport/cancellation ambiguity, mark outcome unknown and terminal;
- after final step, invalidate the permit and run reconciliation reads.

No tool receives a general normal write-capable SDK client. It receives a plan builder with a read-only client and, after approval, a controlled executor bound to the permit.

## Retry and idempotency

### Automatic behavior

- No mutation auto-retry.
- No automatic replay after 408, 429, 5xx, timeout, connection reset, or cancellation.
- No `Idempotency-Key` safety claim; Clockify evidence says the header is unsupported/no-op.
- Reconciliation reads may use the read retry policy.

### Manual recovery

After `OUTCOME_UNKNOWN`, the result gives an operation-specific read-back action:

- search by returned/known ID;
- list and compare IDs before/after;
- inspect target status;
- inspect invoice payments;
- inspect membership set;
- inspect webhook/token state where possible.

The user may start a new write only after reconciliation. A new call produces a new preview and nonce.

### Idempotent-looking writes

A `PUT` that sets a value to the same value may be server-idempotent in theory, but it is still not automatically retried because:

- Clockify omission semantics can be replacing or mixed;
- the network failure may occur after a concurrent state change;
- the operation may have side effects not represented by the final entity state;
- the evidence does not prove idempotence operation by operation.

The MCP annotation therefore keeps `idempotentHint=false` for writes unless a future independently proven operation warrants a narrow exception. The executor rule still forbids automatic retry.

## Mutation behavior dimensions

Do not use a single `LOW/HIGH` number. Record only dimensions that change preview, precondition, cap, or reconciliation behavior.

| Dimension | Values | Behavior changed |
|---|---|---|
| Effect | create, replace, patch, transition, delete, bulk | preview and execution shape |
| Scope | one entity, explicit set, workspace-wide | count, caps, and blast-radius display |
| Sensitivity | financial, access control, time entitlement, external delivery, general | required fields and warnings |
| Replacement | none, patch, full proven, mixed proven, unknown | required current-state read and field diff |
| Reversibility | reversible, conditional, irreversible, unknown | preview and recovery guidance |
| Read-back | direct, list-diff, indirect, unavailable | reconciliation strategy |
| Lifecycle | none or exact prerequisite sequence | multi-step plan |

A dimension must not exist if no runtime or user-interaction behavior reads it.

## Operation-class rules

### Create

- preview every body field;
- show the parent/workspace;
- no auto-retry;
- prefer returned ID;
- if response does not identify the created entity, use a pre/post list diff only when it is reliable;
- never guess an ID from a parent response.

### Replace

- read current state when possible;
- render a complete field diff, including fields preserved and cleared;
- require all proven replacement fields;
- bind a precondition fingerprint;
- unknown omission semantics are shown as a warning and are not hidden by a partial convenience API.

### Patch

- show only fields actually sent plus their current values when available;
- distinguish explicit null/empty from omitted;
- bind current state for sensitive fields.

### Status transition

- show current and target state;
- reject impossible or no-op transitions locally when evidence proves the transition graph;
- re-read status before dispatch;
- do not combine unrelated transitions into one approval.

### Delete

- show entity identity and current state;
- state irreversibility explicitly;
- include every archive/DONE prerequisite as a separate approved step;
- pending-only withdrawals fail before approval if current status is not pending;
- no automatic rollback of a successfully applied prerequisite after final delete fails.

### Bulk

- canonicalize and bind the complete ID set;
- reject duplicates locally;
- show exact count and complete structured list;
- default soft threshold: 100 entities. Above it, the original tool arguments must explicitly request a large batch and the preview must highlight it;
- default hard cap: 1,000 entities unless an operation-specific lower API limit applies;
- do not paginate a mutation silently beyond the approved set;
- report per-item outcomes and stop rules.

The thresholds are configuration constants with boundary tests, not risk labels.

### Financial

- state exact wire units and human-readable interpretation;
- show current and proposed totals/rates/balances;
- reject ambiguous money units rather than guess;
- payment creation reconciles the new payment ID by list diff and reports `null` if not uniquely recoverable;
- an unreconciled successful payment must not be retried.

### Access, role, membership

- show added/removed users/groups and resulting role set;
- bind stable user/group IDs, not names alone;
- re-read membership before execution;
- workspace-wide or manager-role changes always use explicit set diffs.

### Time entitlement and approvals

- show policy, user, period, current balance/status, and delta;
- balance-assignment create/update is displayed as an additive change where evidence proves that behavior;
- policy-type-dependent request shapes are validated before preview;
- status-note requirements are exact.

### Webhooks and external delivery

- show destination URL, event types, and whether a secret is created/replaced;
- validate callback URLs against the same SSRF/unsafe-host rules used by the SDK helper before preview;
- redact auth tokens and signatures;
- token rotation is irreversible and requires read-back guidance if the response is ambiguous.

### File-bearing writes

Do not expose file upload or expense attachment writes in the first write wave.

Before exposure, prove:

- target clients can supply the intended file content safely;
- size and content-type limits;
- canonical SHA-256 binding of exact bytes;
- replay-safe storage across MRTR rounds;
- no path traversal from filenames;
- preview shows filename, size, type, and digest but not contents;
- the final executor sends the exact approved bytes once.

## Lifecycle plans

### Archive-before-delete example

```text
Step 1: projects.update
  exact replacement body with archived=true
Step 2: projects.delete
  exact project ID
```

The preview states both steps. One permit authorizes only that sequence.

Outcomes:

- step 1 fails: `FAILED`, project unchanged as far as the response proves;
- step 1 succeeds, step 2 succeeds: `SUCCEEDED`;
- step 1 succeeds, step 2 fails: `PARTIAL_FAILURE`, project remains archived;
- connection fails during either step: `OUTCOME_UNKNOWN` for that step and no later step is attempted;
- cancellation between steps: `PARTIAL_FAILURE`, no rollback.

The same structure applies to task `DONE` before delete and any other proven prerequisite. Do not infer prerequisites from entity names; declare them per operation.

## Partial failures and receipts

A write result is structured:

```python
class WriteResult(BaseModel):
    state: Literal[
        "rejected",
        "expired",
        "failed_before_dispatch",
        "failed",
        "outcome_unknown",
        "partial_failure",
        "succeeded",
        "succeeded_unreconciled",
        "reconciled",
    ]
    tool_name: str
    confirmation_id: str
    operation_ids: list[str]
    applied_steps: list[AppliedStep]
    failed_step: FailedStep | None
    data: object | None
    changed: ChangedEntities | None
    warnings: list[str]
    next_actions: list[str]
    request_ids: list[str]
```

Rules:

- `succeeded_unreconciled` means the mutation response succeeded but the read-back failed. It is not a failure and must not prompt a retry.
- `outcome_unknown` means transport evidence cannot prove whether the current step applied.
- `partial_failure` means at least one earlier step definitely applied and a later step did not complete.
- `failed` means a definitive API response rejected the first/current step and no prior step applied.
- request IDs are preserved for support.
- errors never include secrets or raw unbounded upstream bodies.

## Cancellation

| Cancellation point | Required result |
|---|---|
| During validation/read-only preview | no mutation; pending record cancelled/expired |
| While waiting for user | no mutation |
| After approval but before nonce consumption | no mutation |
| After nonce consumption but before dispatch | `failed_before_dispatch`; permit remains consumed |
| During an HTTP mutation | `outcome_unknown` unless the HTTP layer has a definitive response |
| Between lifecycle steps | `partial_failure`; no later step and no automatic rollback |
| During reconciliation read | mutation result preserved as `succeeded_unreconciled` |

Do not catch cancellation and continue dispatching.

## Replay and concurrency scenarios

### Replayed sealed request state

- official boundary accepts it only if all integrity/binding checks pass;
- old nonce is already consumed or absent;
- controlled execution rejects it;
- if the resolver starts a new pending confirmation, its new nonce changes the question and requires a new user answer.

### Two retries race on one approved state

- both reach `consume`;
- one obtains the lock first and receives the permit;
- the other gets `confirmation_already_used`;
- mock Clockify sees one mutation.

### Two identical calls start before approval

- same principal/tool/arguments key and same current plan may share one pending nonce;
- both users/rounds see the same confirmation ID;
- at most one executes;
- the other must begin again for a second identical mutation.

This coalescing is a deliberate anti-duplicate behavior. It is safer than allowing one approval to create two identical entities.

### Same arguments, changed current state

- plan digest changes;
- pending nonce is invalidated;
- question changes;
- recorded answer is not reused;
- user sees a new preview.

### Principal or workspace changes

- request-state principal or argument binding rejects the round;
- nonce store comparison also rejects;
- no mutation.

## Protocol-era compatibility

### 2026-07-28 and later

Expected path:

- `Resolve(Elicit(...))` produces MRTR;
- request state is sealed and verified;
- same-call retry carries recorded answer;
- nonce store adds single-use;
- no server-initiated request.

### 2025-11-25 and earlier

Expected path:

- the same resolver uses synchronous elicitation;
- no modern `InputRequiredResult` is manually returned;
- the in-memory nonce store still binds/consumes once;
- if client capability is absent, fail closed.

### Why manual MRTR is not the default

Manual `InputRequiredResult` would require explicit protocol branching, duplicates interaction logic, cannot be combined with `Resolve` in one call, and fails on legacy sessions if returned unconditionally. It remains acceptable only when a future operation needs a multi-question flow the high-level dependency system cannot represent and that need is separately proven.

### Protocol versions newer than 2026-07-28

Do not compare only for equality. Use the official SDK’s negotiated-version helpers. Tests pin the first MRTR revision while allowing future compatible revisions.

## Target-client compatibility testing

Automated minimum:

1. official Python v2 client in-memory, modern/auto mode;
2. official Python v2 client forced to legacy mode;
3. official Python v2 client with elicitation callback absent;
4. spawned stdio transport with real JSON-RPC framing;
5. repeated and concurrent MRTR rounds;
6. request-state key/process restart behavior.

Before public write release, manually test every intended host product. At least two real target hosts must be recorded. For each host verify:

- it negotiates the expected protocol era;
- it displays the full preview before any Clockify request;
- the approval control is user-facing and not a model-generated tool argument;
- approve, reject, decline, cancel, timeout, and unsupported elicitation behave correctly;
- the host does not silently auto-accept;
- long previews remain readable;
- structured entity lists and money units are visible;
- one approval produces at most one mock/live mutation;
- stderr logging does not corrupt stdio.

A host that cannot satisfy these conditions remains read-only, even if it can call the tool technically.

## Adversarial test catalogue

### Request-state and binding

- tamper one byte of state;
- malformed/non-string state;
- expired state;
- state minted under another process key;
- wrong audience;
- wrong principal;
- different tool name;
- different arguments, including omitted versus null;
- different workspace;
- different protocol method;
- replay valid state before and after nonce consumption;
- volatile preview field causes test failure until removed/stabilized.

### Nonce store

- exact TTL boundary;
- max pending boundary;
- per-plan byte boundary;
- prune before capacity rejection;
- same key/same plan returns same nonce;
- same key/changed plan invalidates old nonce;
- reject, decline, cancel;
- consume once;
- 100 concurrent consumers yield one permit;
- consumed tombstone rejects old nonce;
- restart loses all pending state safely.

### Exact plan enforcement

- change operation ID after approval;
- change method/service/path;
- reorder query pairs where order is meaningful;
- add/remove query field;
- change explicit null to omitted;
- reorder body object keys without changing semantics, which must still match canonical digest;
- change array order, which must not match;
- change money scale;
- change one byte of file content;
- add an unapproved lifecycle step;
- repeat or skip a step;
- attempt a read operation through write permit and a write through read executor;
- attempt destination redirect/custom host after approval.

### State drift

- entity field changes between first and final MRTR round, causing re-prompt;
- entity changes after approval but before dispatch, causing failure;
- entity disappears;
- membership set changes;
- invoice/payment list changes;
- no read route, with explicit warning;
- final read/precondition times out.

### Retry and outcomes

- connect failure before write dispatch;
- write timeout;
- read timeout after server may have applied write;
- connection reset after response body begins;
- 429/500/503 on write, no retry;
- 429/503 on reconciliation read, allowed read retry;
- successful write plus failed reconciliation;
- payment create plus ambiguous list diff;
- cancellation at every state-machine boundary.

### Lifecycle and partial failure

- archive required and already archived;
- archive step failure;
- archive success/delete failure;
- archive success/delete timeout;
- task DONE prerequisite;
- pending-only time-off withdrawal rejected before preview;
- concurrent state change after archive;
- no rollback mutation occurs without a second explicit plan.

### Sensitive classes

- financial unit mismatch rejected;
- full replacement omitted field highlighted/rejected;
- bulk duplicate IDs rejected;
- bulk soft/hard thresholds;
- membership names resolve to stable IDs;
- secret redaction while request digest changes when secret changes;
- unsafe webhook URL rejected before preview;
- response content containing prompt-injection text is returned as untrusted data, not executed as instructions.

### Protocol/client

- modern Resolve path;
- legacy Resolve path;
- unsupported elicitation;
- client round limit;
- real stdio output cleanliness;
- target-host approve/reject/cancel evidence.

## Implementation sequence

### Safety Phase A — Pure plan and canonicalization

Implement immutable plan types, canonical encoding, preview rendering, and request compiler integration. Use fixtures only. No MCP server and no write executor.

Acceptance: same semantic request produces same digest; every material wire change produces a different digest; previews are deterministic and redact secrets.

### Safety Phase B — Nonce store

Implement bounded in-memory state transitions and concurrency tests.

Acceptance: one permit from 100 concurrent consumers; expiry/capacity boundaries; stable nonce across repeated preparation; changed plan gets a new nonce.

### Safety Phase C — MCP resolver integration

Wire `PreparedWrite`, `Resolve(Elicit(...))`, request-state security, and custom principal binding into a fake no-op tool.

Acceptance: modern and legacy flows; unsupported client fails closed; replay reaches no mock write.

### Safety Phase D — Controlled executor

Implement exact permit/step enforcement against a mock HTTP sender.

Acceptance: only exact approved request dispatches; one permit, one ordered plan; mismatch cases fail before sender.

### Safety Phase E — Precondition, outcome, reconciliation

Implement state fingerprints, final checks, result states, cancellation, and read-back adapters.

Acceptance: every state-machine terminal result is exercised; no retry on ambiguous write.

### Safety Phase F — Independent review

A reviewer who did not implement the gate receives:

- this plan;
- safety source and tests;
- an adversarial harness that attempts direct/mismatched/replayed/concurrent calls;
- protocol and target-client receipts.

All findings are fixed in the design and tests. A review checklist alone is not completion.

### Safety Phase G — First real write

Choose one single-entity additive write with direct read-back and no multipart. Implement it end to end. Do not batch several tools into the first proof.

Only after that tool passes all generic and operation-specific tests may later writes follow the behavior-based waves in the master plan.

## Conditions required before writes ship

All are mandatory:

- [ ] Read MCP is independently complete and structurally read-only.
- [ ] Official MCP v2 modern and legacy resolver behavior is pinned by tests.
- [ ] `RequestStateSecurity` uses a process key, five-minute TTL, audience, and custom principal binding.
- [ ] Nonce store is bounded, atomic, expiring, and true single-use under concurrency.
- [ ] Exact canonical arguments and wire-plan binding is proven.
- [ ] Controlled executor refuses every mismatch and unapproved step.
- [ ] No mutation auto-retry exists below or above the gate.
- [ ] State drift, cancellation, partial failure, and unknown outcome are represented correctly.
- [ ] Sensitive values are redacted from preview, errors, and logs.
- [ ] Operation-specific preview, lifecycle, unit, and reconciliation tests pass.
- [ ] Real stdio test passes.
- [ ] At least two intended real hosts show the exact user-facing approval and fail closed when unsupported.
- [ ] An independent adversarial reviewer approves the implementation.
- [ ] The first live mutation proof runs only in a sacrificial workspace and leaves no residue.

Until every box is true, write tool registration remains disabled or absent.

## Explicit unresolved points

These are not implementation guesses:

1. **Target-host human approval guarantee:** protocol support does not prove UI behavior. Resolve through compatibility testing before release.
2. **Operations without reliable read-back:** keep them unexposed or return clearly unreconciled results; do not invent IDs.
3. **Residual Clockify race:** without conditional writes, final read and mutation are not atomic. State this in affected previews.
4. **Remote/multi-worker deployment:** requires shared keys, shared atomic store, and real authenticated principal. It is a separate product milestone.
5. **File-bearing MCP writes:** remain deferred until exact bytes can survive the interaction flow safely.
6. **Any write whose money, replacement, lifecycle, or permission semantics remain unresolved:** SDK method may exist, but MCP tool does not ship.

## Final safety standard

A safe MCP write is not “a write tool with a warning.” It is an exact, deterministic, user-visible plan whose identity and arguments are protected by the protocol, whose single use is atomically enforced by the server, whose dispatched bytes are constrained by a consumed permit, and whose uncertain outcomes are never blindly retried.
