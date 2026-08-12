# Claude Code Mission: Implement the Complete Clockify Python SDK + MCP

You are the principal implementation engineer for a new repository. This is an **implementation run**, not another planning, audit, or proposal run.

Build the complete Python-native successor described by the authoritative blueprint files. Work autonomously from the empty project directory through tested, installable code. Do not stop after creating a skeleton, a partial proof of concept, a report, or another implementation plan.

The desired result is deliberately boring, explicit, high-quality software: complete, correct, small enough to understand, easy to modify, strongly tested, and free of process bureaucracy.

---

## 1. Fixed operating context

Expected project directory:

```text
~/Downloads/working/addons-me/2mcp
```

Expected read-only TypeScript reference repository:

```text
~/Downloads/working/addons-me/clockify-ts-sdk
```

Resolve both paths with `pwd -P` / `realpath` before doing anything. The directory name `2mcp` is only the local working-directory name. The Python distribution and imports must use the names required by the blueprint.

### Persistent write boundary

You may create, edit, delete, test, build, and initialize Git **inside `2mcp` only**.

You may use OS temporary directories for disposable wheel-install tests and other ephemeral test environments.

The sibling `clockify-ts-sdk` repository is **read-only evidence**. Never edit it, generate into it, run a command that rewrites it, install files into it, clean it, commit it, change its branch, stash it, or reset it. Record its initial tracked Git status and exact HEAD. Verify at major checkpoints that its tracked state remains unchanged.

Do not write persistent files elsewhere under `addons-me`.

---

## 2. Authoritative inputs and precedence

The project must contain these exact planning files under `docs/port/`:

```text
docs/port/MASTER_IMPLEMENTATION_PLAN.md
docs/port/OPERATION_PORT_MANIFEST.md
docs/port/MCP_WRITE_SAFETY_PLAN.md
```

Expected SHA-256 values:

```text
MASTER_IMPLEMENTATION_PLAN.md
98cd9d525d6b90d7c0f8fd72df04d4c30a43d1034d00a25d7b050cbe983f9513

OPERATION_PORT_MANIFEST.md
c980a24fcf87c91b504a500744e1c8a3cda9b5116a78135769695d45a30e2846

MCP_WRITE_SAFETY_PLAN.md
f278b1ddbcd846b31e31d54ccd9942b460f13bf0e5fc5e16943d0b6ded200311
```

If they are not already in `docs/port/`, search under `~/Downloads` by exact filename and copy the matching files into `docs/port/`. Do not move or rewrite the source copies. If multiple candidates exist, use the hashes above.

The corrected OpenAPI should normally be read from:

```text
../clockify-ts-sdk/spec/corrected/clockify.corrected.openapi.yaml
```

Expected SHA-256 at the plan anchor:

```text
38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
```

The TypeScript discrepancy evidence is normally at:

```text
../clockify-ts-sdk/spec/evidence/discrepancies.md
```

Use this authority order:

1. `MASTER_IMPLEMENTATION_PLAN.md` owns architecture, sequencing, maintenance, gates, and the implementer contract.
2. `OPERATION_PORT_MANIFEST.md` owns all 168 endpoint records, exact public resource/method mappings, schemas, wire names, response handling, lifecycle notes, and unresolved points.
3. `MCP_WRITE_SAFETY_PLAN.md` owns every MCP mutation-safety invariant and ship condition.
4. The corrected OpenAPI, discrepancy ledger, focused TypeScript implementation, fixtures, and tests provide evidence when a plan entry needs implementation detail.
5. Current official MCP Python v2 source/documentation is authoritative for the actual installed MCP API. Inspect the installed package source and official primary sources when signatures or behavior differ from the pinned plan evidence.

Do not silently override the blueprint because the TypeScript repository uses a different architecture. Port its proven Clockify knowledge, not its generator/governance machinery.

If the sibling TypeScript HEAD differs from the blueprint anchor `d7091a44a1b95d4918fa17a7f9b174bf668a9136`, inspect the diff for newer product/API evidence. Do not let unrelated newer governance changes reshape this Python repository. Record material evidence changes in `IMPLEMENTATION_STATUS.md` and integrate only the supported correction.

---

## 3. Execution mandate

You have permission to:

- initialize a local Git repository in `2mcp` if one does not exist;
- install Python/tool dependencies with `uv`;
- create all source, tests, docs, scripts, workflows, and package files required by the blueprint;
- use focused parallel subagents for independent read-only investigation or review;
- run mock, unit, integration, stdio, build, wheel-install, and live sandbox tests;
- make local commits after coherent green phases;
- use the sacrificial Clockify credentials already present in the environment;
- make any Clockify API call needed to resolve uncertainty or prove behavior **within the live-sandbox rules below**.

Do not ask for approval after each phase. Do not wait for the user to choose routine implementation details. Investigate, make the weakest evidence-backed decision, implement it, and continue.

Only stop a line of work when a physical prerequisite is absent or a behavior remains genuinely unprovable after source inspection and safe live probing. Continue every independent part of the implementation. Record the exact blocker rather than inventing behavior.

Never claim completion based on intention. Completion requires code plus the required passing commands.

---

## 4. Restartability without bureaucracy

This implementation must survive context compaction, rate limits, and a fresh Claude Code session without depending on chat history.

### Create two small continuity files

#### `CLAUDE.md`

Create a concise repository-local Claude guide. It must:

- point to the three authoritative files in `docs/port/` instead of copying them;
- state the write boundary and sibling-repo read-only rule;
- state the non-negotiable architecture and final gates;
- state the startup/resume ritual below;
- remain compact and durable; do not turn it into a second master plan or a historical diary.

#### `IMPLEMENTATION_STATUS.md`

Maintain one live status page, preferably under 250 lines. It must contain only:

```text
Goal
Blueprint hashes
Reference repo HEAD and initial tracked status
Current phase and current acceptance target
Completed phases with local commit hashes
Last known green commands
Current work in progress
Unresolved evidence questions / real blockers
Live-test run ID and artifact cleanup status
Material design deviations from the blueprint, with evidence and tests
Next exact action
```

Update it:

- after each coherent phase becomes green;
- before deliberate context compaction or session termination;
- whenever a real blocker or blueprint deviation appears;
- after every live mutation campaign, including final residue count.

Do **not** append a chronological transcript of every command. Git history and tests are the proof.

### Startup/resume ritual

At the start of this run and every fresh session:

1. Resolve the project and sibling paths.
2. Read `CLAUDE.md`.
3. Read the master plan and write-safety plan headings plus the sections for the current phase.
4. Read `IMPLEMENTATION_STATUS.md`.
5. Run `git status --short` and inspect the last five local commits.
6. Check the sibling reference repository has not been modified.
7. Run the narrowest test/gate that proves the current checkpoint still holds.
8. Continue from `Next exact action`; do not redesign completed architecture.

Use local commits as durable phase checkpoints. Make one focused commit after a phase or substantial coherent wave is green. Never commit secrets, live payloads, caches, virtual environments, build outputs that should be ignored, or temporary probes.

Do not push, publish, create releases, or modify a remote unless the user separately gives an explicit target and asks for it.

---

## 5. Engineering philosophy

Apply these rules continuously:

- **No overengineering.**
- **No dead code.**
- **No placeholder production paths.**
- **No abstraction without a present concrete purpose.**
- **No governance for its own sake.**
- **No hidden magic.**
- **No false completeness.**

Optimize for:

- correctness;
- complete API coverage;
- explicit behavior;
- local reasoning;
- maintainability by humans and coding agents;
- clear names and conventional Python structure;
- fast deterministic tests;
- network correctness and connection reuse;
- precise failure modes;
- minimal dependency and operational burden.

Prefer explicit functions and small dataclasses over metaprogramming. Prefer one invariant at the correct boundary over repeated downstream checks. Prefer deleting a helper over keeping a generic abstraction that has one caller and hides behavior.

Comments and docs should explain non-obvious **why**, wire quirks, units, replacement/lifecycle hazards, and safety boundaries. Do not narrate obvious syntax.

User-facing prose must use plain, direct technical English.

### Forbidden architecture and tooling

Do not introduce:

- runtime OpenAPI loading;
- dynamically generated public SDK methods;
- runtime-generated MCP tool functions;
- `__getattr__` public API tricks;
- import-time registration side effects or filesystem scanning;
- a generic CRUD framework;
- a generic MCP “call any operation” mutation tool;
- a synchronous SDK facade;
- a CLI product;
- Redis, a database, queues, distributed locks, durable jobs, or background workers for local stdio;
- response caching;
- automatic mutation retry;
- a claimed idempotency guarantee based on an unsupported header;
- `orjson`, `tenacity`, `datamodel-code-generator`, `jsonschema`, a DI framework, or telemetry SDKs without a new accepted requirement that cannot be met more simply;
- giant policy/contract/receipt inventories, docs-count checks, currentness gates, mutation-testing requirements, pack snapshots, or a large Makefile/task-runner layer;
- tests whose only purpose is proving that another test/check/file exists.

No `TODO`, `pass`, `NotImplementedError`, fake return value, or silent `Any` is acceptable in a claimed-complete production path.

---

## 6. Non-negotiable product end state

Preserve all blueprint decisions unless direct evidence falsifies one and the replacement is simpler and equally strong.

### Repository and package

One repository and one distribution:

```text
Distribution: clockify-python-115
SDK import:  clockify
MCP import:  clockify_mcp
Console:     clockify-mcp
Python:      >=3.11
Build:       hatchling / PEP 517 and 621
Environment: uv
```

One wheel contains both import packages. MCP runtime dependencies are optional through the `mcp` extra.

### SDK

- One async-first `ClockifyClient`.
- One reused `httpx.AsyncClient` by default, with explicit injected-client ownership.
- Exactly one configured credential: `api_key` or `addon_token`.
- Exactly **168** reconciled operations.
- Exactly **29** explicit resource attributes.
- Exactly **168** explicit public resource methods with the exact unique resource/method mapping in the operation manifest.
- Exactly **62** non-mutating operations and **106** mutating operations.
- Read split: **49 GET reads + 13 semantic POST reads**.
- Exactly **339 reachable component-schema roots**, plus required inline schemas, represented as reviewed committed Pydantic v2 source.
- Python aliases use snake_case; exact wire keys are preserved.
- Request models reject unknown fields; response models retain additive unknown fields.
- No global datetime coercion or money normalization that destroys Clockify semantics.
- Public methods return typed models, typed pages/lists, bytes/text/`None`, not untyped dictionaries everywhere.
- A bounded, explicit raw operation escape hatch exists for SDK users, but it cannot send an arbitrary URL.

### Operation model and HTTP boundary

Maintain one permanent, explicit operation record per endpoint, grouped into 29 domain modules. Each record contains only fields with active runtime consumers: stable ID, resource/method mapping, HTTP method, service, path, path/query metadata, request encoding, response kind, pagination, and semantic mutation/lifecycle/replacement information.

The executor must prove:

- three default services:
  - `https://api.clockify.me/api/v1`;
  - `https://reports.api.clockify.me/v1`;
  - `https://auditlog-api.api.clockify.me/v1`;
- final destination validation occurs before an auth header is attached;
- redirects are disabled;
- custom hosts require explicit opt-in;
- caller headers win over defaults;
- path and query serialization are exact;
- JSON, multipart, bytes, text, content-negotiated, and no-content responses work;
- every response is closed;
- cancellation propagates;
- safe read retry, if implemented, is semantic-operation based rather than verb based;
- no write is automatically retried;
- a transport failure after mutation dispatch becomes an unknown outcome that requires read-back before any manual retry.

### Read MCP

Implement with the official MCP Python v2 stack and `MCPServer`.

- Exactly **60** eligible raw read tools, explicitly implemented and registered.
- Two binary-only reads remain SDK-only.
- Public shared-report view permits JSON/CSV and rejects binary formats before network.
- Exactly five curated read workflows:
  - `clockify_status`;
  - `clockify_workspace_overview`;
  - `clockify_review_day`;
  - `clockify_review_week`;
  - `clockify_doctor`.
- Every raw read and workflow sub-call uses a client built over the final-boundary `ReadOnlyExecutor`.
- A deliberately miswired mutation must fail before any HTTP request.
- Tool annotations are accurate hints only, never the security boundary.
- Server construction performs no Clockify request.
- Stdout is MCP protocol traffic only; logs go to stderr.
- Real spawned-stdio smoke tests are required.

### MCP writes

SDK writes do not automatically become MCP writes.

Implement the write-safety core exactly from `MCP_WRITE_SAFETY_PLAN.md` before exposing a single write tool:

- model-invisible confirmation through `Annotated[..., Resolve(...)]` and `Elicit`;
- modern MRTR behavior plus supported legacy behavior from the official SDK;
- official `RequestStateSecurity`, not custom cryptography;
- process-local request-state key scope suitable for stdio;
- custom principal binding;
- deterministic exact preview built only from validated arguments and read-only current-state queries;
- canonical exact wire-plan digest;
- bounded expiring in-memory nonce store;
- atomic consume before the first mutation dispatch;
- exact ordered `ExecutionPermit`;
- final `ControlledWriteExecutor` that cannot dispatch anything outside the consumed permit;
- final precondition check and explicit state-drift failure;
- no automatic mutation retry;
- explicit partial failure, outcome unknown, succeeded-unreconciled, and reconciliation states;
- secret redaction;
- exact concurrency and replay tests.

Do not translate the TypeScript `dry_run` / `confirm_token` store. Do not expose a model-supplied `confirm`, approval token, or generic write switch.

Implement the safety core and write adapters as far as evidence permits. However, the default shipped server must remain structurally read-only until every mandatory ship condition in the safety plan is actually proven, including target-host human approval UI and an independent adversarial review. Code existence is not release authorization.

Use separate, obvious server construction for read-only and full/approved modes rather than a boolean that bypasses safety. Do not call writes “safe” merely because they are disabled by configuration.

---

## 7. Implementation method

Follow the ten phases in `MASTER_IMPLEMENTATION_PLAN.md` in order. You may batch independent files and use parallel read-only subagents, but one main implementation thread owns architecture and integration.

Do not re-plan the repository. At the start of each phase, read that phase’s objective, files, invariants, tests, acceptance criteria, and “must not build” list. A phase is complete only when its acceptance criteria are demonstrated.

### Phase 0: evidence and framework seams

- Verify blueprint hashes, OpenAPI hash, exact surface counts, unique Python mappings, and the reference HEAD.
- Inspect the current official MCP package API rather than guessing imports or signatures.
- Use temporary executable spikes only for genuinely uncertain Pydantic/MCP seams.
- Prove modern and legacy resolver behavior, request-state binding, replay needing nonce consumption, and stdout-clean stdio.
- Delete temporary spikes after integrating conclusions.

Do not mutate Clockify in Phase 0.

### Phase 1: minimal repository skeleton

Create only the minimal package, docs, tests, CI, security, and build structure specified by the master plan. Configure Python 3.11+, hatchling, uv, ruff, pyright, pytest, and the optional MCP extra.

Do not add pre-commit, a Makefile alias farm, coverage policy, or release ceremony.

### Phase 2: models and operation registry

- Build the small deterministic OpenAPI model importer.
- Generate readable committed Pydantic v2 model modules for all 339 reachable roots and required inline schemas.
- Refuse unsupported constructs rather than emitting silent `Any`.
- Hand-author explicit static operation constants grouped by domain.
- Build explicit `ALL_OPERATIONS`, `BY_ID`, and public-method maps.
- Tests pin 168/62/106/49/13, three service counts 157/10/1, exactly three multipart operations, uniqueness, request-extra rejection, and response-extra preservation.

The importer may generate static models only. It must never generate resources, MCP tools, workflows, CI, release files, or governance.

### Phase 3: HTTP foundation

Implement and exhaustively test the transport metadata combinations in the operation registry with `httpx.MockTransport`.

Keep request compilation pure where possible so the exact compiled request can later be used by MCP write-plan binding.

Do not build a sync client, cache, generic arbitrary-URL sender, or write retry.

### Phase 4: all 168 SDK methods

Implement every manifest method explicitly. Use concise typed wrappers over operation execution, not 168 copies of HTTP logic.

Create a 168-case public wiring suite that calls the actual public methods and verifies operation ID, host, method, path, query, body encoding, and response adaptation. Do not substitute a test that merely compares two metadata files.

A domain wave is not complete while any operation in it lacks a public request-construction test.

### Phase 5: proven Clockify semantics

Port the behavior, not the old proof machinery. Add focused regression tests for the deviations required by the master plan and manifest, including hosts, semantic POST reads, pagination variants, envelopes, money scales, replace/mixed omission, lifecycle prerequisites, absent single-get routes, payment-ID recovery, exact weekly intervals, wall-clock windows, binary handling, and unsupported idempotency behavior.

Raw update methods must remain honest about replacement risk. Add safe read-modify-write helpers only where live evidence proves the exact fields and the helper prevents a real data-loss trap.

### Phase 6: structural read MCP

Implement and prove all 60 raw read tools with the hard `ReadOnlyExecutor` boundary. No write module may be imported or registered by the read server.

### Phase 7: five read workflows

Implement only the five named workflows. They must use bounded pagination, explicit time windows/timezones, and the restricted client. Do not add docs-search, plan-runner, demo-data, or model-summary bureaucracy.

### Phase 8: write-safety core, no registered writes

Implement every safety phase and adversarial test in the companion safety plan. Use a fake/no-op write first. Prove that no mutation reaches even a mock HTTP sender without a valid, unconsumed, exact-plan permit and that one permit cannot dispatch twice.

Use a fresh-context reviewer subagent that did not author the gate to attack it. The reviewer must inspect source and run adversarial tests, not only read a checklist. Store one concise review at `docs/mcp-write-safety-review.md`. Fix every valid finding before continuing. State clearly that a same-vendor subagent is fresh-context review, not proof of independent human approval.

### Phase 9: MCP writes in behavior-based waves

Do not mechanically register 106 write tools at once.

Proceed in the exact behavioral waves in the master plan. For every candidate write:

- explicit typed tool function;
- exact underlying operation/ordered lifecycle steps;
- deterministic structured and human preview;
- exact argument/workspace/principal/wire-plan binding;
- current-state fingerprint where possible;
- explicit read-back or explicit lack of reliable read-back;
- correct unknown/partial/unreconciled outcomes;
- focused safety and operation-specific tests;
- no registration if money, replacement, lifecycle, permission, file, or read-back semantics remain unresolved.

Prefer `tags.create` as the first live additive proof if current evidence still confirms it is single-entity, directly readable, and safely cleanable. Otherwise choose the simplest operation that satisfies Safety Phase G. Do not use an unresolved or multipart write for the first proof.

Continue through later waves as far as evidence and target-client support permit. Do not use a missing target-host UI proof as an excuse to leave the SDK, read MCP, safety core, or write adapters incomplete. Keep release registration read-only when the ship conditions are not all met.

### Phase 10: packaging and release proof

Finish concise user docs, examples, minimal workflows, build, exact wheel installation, import smoke, and console smoke. Do not publish.

The installed wheel—not the working tree—is the final artifact under test.

---

## 8. Use of subagents

Use subagents selectively where parallelism improves evidence or review without fragmenting architecture.

Good uses:

- one read-only operation/schema reconciliation agent;
- one TypeScript discrepancy/test mining agent for a specific domain wave;
- one transport/test adversary;
- one fresh-context MCP write-safety adversary;
- one final completeness auditor mapping manifest operations to public methods/tools/tests.

Bad uses:

- multiple agents independently inventing architecture;
- one agent per trivial file;
- merging generated bulk code without main-thread review;
- treating subagent assertions as proof without source or command evidence.

Require subagents to return exact file paths, symbols, tests, and evidence. The main thread validates and integrates all findings.

---

## 9. Live Clockify sandbox authority and rules

Environment variables are expected to include:

```text
CLOCKIFY_API_KEY
CLOCKIFY_WORKSPACE_ID
```

An add-on token may exist, but use exactly one credential. Never print, echo, serialize, commit, log, or include credential values in test output. Do not run shell tracing around secret-bearing commands. Presence checks must reveal only set/unset status.

The workspace is sacrificial and live calls are authorized, including mutations, but live testing must still be deterministic and clean.

### Live-test rules

1. Confirm the configured workspace ID is the workspace actually reached before mutating.
2. Resolve the current user through the API rather than requiring a user ID in source.
3. Generate one unique run prefix such as `py115-<UTC-date>-<random>`.
4. Read existing workspace data as needed, but do not mutate unrelated pre-existing objects merely because the workspace is sacrificial.
5. For destructive/lifecycle tests, create the entity and prerequisites in the same run, capture returned IDs, execute the behavior, and clean all residue.
6. Keep a live artifact ledger in memory/test output and summarize only safe IDs/types/status in `IMPLEMENTATION_STATUS.md`; never store raw customer-like payloads or secrets.
7. Cleanup runs in `finally` and must preserve the primary failure. A cleanup failure is an additional explicit failure, not a replacement error.
8. Apply proven archive/DONE/status prerequisites before deletion when required.
9. Never mass-delete objects by broad filter. Delete only exact IDs created by the test run or exact pre-existing test artifacts carrying this run’s unique prefix.
10. After every live mutation campaign, query for the unique prefix and record a final residue count. Green requires zero residue, or a precise externally imposed reason and exact remaining IDs.
11. Keep all live tests under the `live` marker and outside ordinary CI.
12. A plan/permission/product-tier rejection is evidence about environment support, not automatic proof of an SDK bug. Preserve the response safely and continue with mock/contract proof.
13. Use live calls to resolve genuine uncertainties and prove representative host/encoding/lifecycle/money/write behavior. Do not create a recurring live-currentness bureaucracy.

You may build temporary local probe scripts inside a gitignored project temp directory. Delete them when the behavior is encoded in production code and a focused regression test.

---

## 10. Evidence discipline

For every material uncertainty:

1. state the weakest hypothesis consistent with the blueprint and source;
2. inspect the exact OpenAPI operation and relevant TypeScript implementation/tests/evidence;
3. use a safe live probe when source evidence is insufficient and the sandbox can answer it;
4. implement only what the evidence supports;
5. add the focused test that would fail if the behavior regresses;
6. record unresolved behavior plainly rather than guessing.

Do not trust names, verbs, or old comments over actual wire behavior.

Mandatory stop-and-investigate cases include:

- corrected OpenAPI and live behavior disagree;
- a schema requires silent `Any`;
- a route, response type, money unit, pagination envelope, or status code is uncertain;
- a PUT omission rule is unproved;
- a single-get route may be phantom;
- a write preview cannot be deterministic;
- a write lacks read-back/reconciliation;
- a retry may occur after mutation dispatch;
- a target MCP host might auto-accept or hide elicitation;
- an abstraction is justified only by hypothetical future work.

“Stop and investigate” means stop that unsafe guess, not stop the whole implementation.

---

## 11. Testing and quality requirements

The normal local loop must remain:

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q -m "not live"
```

Use focused tests during implementation, then run the complete non-live suite at coherent checkpoints.

Required proof includes:

- model importer fixtures and fail-closed unsupported constructs;
- all model imports/rebuilds;
- registry counts, uniqueness, public mapping, three hosts, multipart count, and semantic read/write classification;
- every request/response class;
- exact query aliases/list styles and omitted-vs-null behavior;
- auth exclusivity, redaction, host validation, redirect refusal, caller-header precedence, timeout, cancellation, and retry boundary;
- all 168 actual public resource methods through request-construction tests;
- every retained discrepancy class;
- pagination loop/incomplete guards;
- all 60 raw MCP read tools and the final write rejection boundary;
- five workflows;
- in-memory MCP and spawned real stdio;
- every write-safety adversarial case before write registration;
- clean wheel and sdist build;
- exact built-wheel installation into a fresh environment;
- SDK import and `clockify-mcp --help` smoke from that environment.

Do not chase a coverage percentage. Add tests for meaningful behavior and contracts. Do not require mutation testing.

A failed test must be fixed or accurately documented as an external live-environment limitation. Never delete or weaken a valid test merely to get green.

---

## 12. Maintainability acceptance

Before calling the repository complete, prove that an ordinary endpoint addition is boring:

```text
1. add or edit one operation record in its domain module;
2. add or edit the relevant static model/import;
3. add or edit one explicit resource method;
4. add the focused SDK test and, when eligible, an explicit MCP tool/test.
```

If normal endpoint work requires changing many unrelated files, redesign that hotspot before finalizing.

Run a final adversarial maintainability audit:

- Can a human locate auth, routing, request compilation, an operation, its resource method, its MCP tool, and its test from names alone?
- Is there one source of runtime operation truth rather than duplicated manifests?
- Is any module an unrelated several-thousand-line dumping ground?
- Is any generic helper harder to understand than its callers?
- Is any abstraction unused or speculative?
- Is any safety property enforced only in prose or annotation?
- Can the sibling TypeScript governance layer be found accidentally translated into this repository?
- Are all 168 operations accounted for without hidden generation?

Delete unnecessary machinery discovered by this audit, then rerun the final gates.

---

## 13. Local Git discipline

If the project is not already a Git repository, initialize one after the three blueprint files are in place.

Use focused local commits after green milestones, for example:

```text
chore: bootstrap clockify-python package
feat(models): add complete static Clockify schema surface
feat(transport): implement authenticated multi-host executor
feat(sdk): complete explicit resource surface
feat(mcp): add structural read-only server
feat(mcp): add read workflows
feat(mcp-safety): add exact single-use write gate
feat(mcp-writes): add reviewed write wave ...
docs: finish package and MCP guidance
```

These are examples, not mandatory wording. Do not make a commit while its phase tests are red. Do not rewrite history merely to make the log prettier. Never touch the sibling repository.

---

## 14. Exact final gates

Before the final completion claim, run from the project root:

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q -m "not live"
uv build
```

Then install the exact built wheel into a new clean temporary environment and prove:

```bash
python -c "from clockify import ClockifyClient; print(ClockifyClient.__name__)"
clockify-mcp --help
```

Run the live suite separately when credentials are present:

```bash
uv run pytest -q -m live
```

Do not let a live environment limitation make the deterministic non-live suite red. Do not claim a live behavior passed unless the command actually passed and cleanup reached zero residue.

For any release mode that registers MCP writes, additionally prove every mandatory condition in `MCP_WRITE_SAFETY_PLAN.md`, including real target-client approval UI evidence. No other test substitutes for those conditions.

---

## 15. Completion report

At the end, return a compact evidence-based report containing:

1. final local Git commit hash and clean/dirty status;
2. implemented distribution/import/console names;
3. exact counts:
   - operations;
   - resources and public SDK methods;
   - reads/writes and GET/POST reads;
   - reachable models;
   - raw MCP reads;
   - read workflows;
   - implemented and actually registered MCP writes;
4. architecture summary in no more than ten lines;
5. exact final commands and exit results;
6. built artifact names and clean-wheel smoke result;
7. live calls performed, safe entity types/IDs, and final residue count;
8. MCP write status:
   - safety core complete/incomplete;
   - write adapters complete/incomplete;
   - registration enabled/disabled;
   - exact unmet ship conditions, if any;
9. genuine unresolved API facts or external constraints;
10. confirmation that the sibling TypeScript repository remained unchanged.

Do not pad the report with a narrative of every file touched. Do not claim “complete” when any required count, test, artifact, cleanup, or safety condition is missing.

---

## 16. Begin now

Start by:

1. resolving and validating both directories;
2. locating and hashing the three blueprint files;
3. recording the sibling repository HEAD/status;
4. reading the master plan’s perfect end state, architecture, implementation phases, definition of done, and implementer contract;
5. reading the operation manifest’s reconciled surface and resource map;
6. reading the write-safety plan’s invariants, components, state machine, adversarial catalogue, and ship conditions;
7. creating `CLAUDE.md` and `IMPLEMENTATION_STATUS.md`;
8. initializing Git if needed;
9. executing Phase 0 and continuing through the implementation.

Do not answer with a plan. Build the repository.
