# Clockify Python — Master Implementation Plan

**Status:** authoritative implementation blueprint for a new repository. This document does not implement the repository and does not authorize changes to `apet97/clockify-ts-sdk`.

**Companion authorities:**

1. `OPERATION_PORT_MANIFEST.md` owns the endpoint-by-endpoint port contract.
2. `MCP_WRITE_SAFETY_PLAN.md` owns MCP mutation safety.
3. This file owns architecture, sequencing, maintenance, quality gates, and the final implementer contract.

## Evidence basis and epistemic key

This plan was reconciled against:

- `apet97/clockify-ts-sdk` at exact commit `d7091a44a1b95d4918fa17a7f9b174bf668a9136`;
- the corrected Clockify OpenAPI whose SHA-256 is `38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94`;
- the repository discrepancy ledger, focused regression tests, MCP tools, and live-evidence records;
- Model Context Protocol specification revision `2026-07-28` from the official specification repository at commit `b25c0874bf0ba699a58e21ef06f659d839659de3`;
- official `modelcontextprotocol/python-sdk` v2 documentation and source at commit `6e304527a54a702fed84066bde8b7d8ce9cfeba7`, including `docs/handlers/dependencies.md`, `docs/handlers/multi-round-trip.md`, `docs/whats-new.md`, and `src/mcp/server/request_state.py`.

Terms in this plan:

- **FACT** — directly supported by the sources above.
- **INFERENCE** — the weakest conclusion that follows from those facts.
- **PROPOSAL** — a design choice for the Python successor.
- **UNRESOLVED** — evidence is not strong enough to turn the point into a hidden requirement.

## Perfect end state

The finished repository is a small Python monorepository that publishes one distribution and contains two import packages:

```text
clockify-python
├── clockify       # complete async Python SDK
└── clockify_mcp   # complete read MCP plus independently approved writes
```

“Done” means all of the following are true:

1. The SDK exposes **all 168 reconciled Clockify operations** through **29 explicit resource objects** and unique, meaningful Python method names.
2. The operation registry classifies **62 operations as non-mutating** and **106 as mutating** by behavior, not by HTTP verb. The 62 reads consist of 49 `GET` operations and 13 body-based `POST` searches/reports.
3. A normal SDK user can call writes directly. The SDK does not impose MCP confirmation on reviewed application code.
4. The read MCP exposes **60 raw read tools**. Two binary-only reads remain SDK-only. Public shared-report viewing is MCP-eligible only for JSON or CSV output.
5. The read MCP also exposes five deliberately small tools with clear user value: status, workspace overview, day review, week review, and doctor.
6. Every MCP read call, including every workflow sub-call, goes through a final `ReadOnlyExecutor` that refuses a mutating operation before the HTTP executor is reached.
7. MCP writes remain absent until the safety milestone in `MCP_WRITE_SAFETY_PLAN.md` is complete and independently proven.
8. The HTTP core reuses one `httpx.AsyncClient`, routes to the three proven Clockify services, validates the authenticated destination before attaching credentials, preserves caller headers, handles JSON/multipart/binary/text/no-content responses, and never automatically retries a write.
9. Known Clockify deviations are encoded as ordinary implementation and focused regression tests. The repository does not recreate the TypeScript evidence-ledger, generated-manifest, policy, and currentness-gate machinery.
10. The ordinary local loop is:

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q -m "not live"
```

11. A fresh developer can clone, install, test, run the MCP over stdio, and use the SDK without running a generator or learning repository-specific ceremony.
12. Adding an ordinary endpoint normally changes one operation module, one model module or model import, one resource module, and one focused test file. It does not require a repository-wide cascade.

## Reconciled facts that govern the architecture

| Fact | Architectural consequence |
|---|---|
| The corrected surface has exactly 168 operations on three hosts. | One permanent operation registry covers the whole SDK and both MCP boundaries. |
| Thirteen `POST` operations are reads. Twelve currently carry misleading write-risk metadata. | `mutates` is a reviewed semantic field. It is never inferred from the verb or copied from `x-clockify-risk`. |
| The API uses JSON, three multipart requests, binary downloads, text/CSV, content-negotiated exports, and empty success bodies. | Response and request encoding are explicit operation fields. There is no JSON-only executor. |
| Pagination names and envelopes differ by operation. `Last-Page` is authoritative where present. | Pagination is declarative per operation. There is no global `page-size` assumption. |
| Clockify money fields use several incompatible scales. | Values remain in documented wire units. Helpers have unit-specific names and never silently normalize every amount. |
| Several `PUT` operations are replacing, some have mixed omission behavior, and some remain unresolved. | Replacement semantics are recorded per operation. Verb-wide “PUT means replace” logic is forbidden. |
| Clockify does not provide effective idempotency-key support. | No write is automatically retried. MCP never claims a write is safely repeatable because a header was sent. |
| Some single-resource routes are absent or return 404/405; safe lookup sometimes requires list-and-filter. | Resource helpers implement the proven lookup route instead of inventing a missing endpoint. |
| The TypeScript repository contains 303 scripts and 185 Make targets around a 168-operation product. | The Python repository uses focused product tests and minimal CI, not a translated governance system. |
| MCP Python SDK v2 uses MRTR and sealed `requestState`, but request-state integrity does not atomically consume a confirmation. | MCP writes use the SDK’s interaction mechanism plus a small server-side atomic nonce store. |
| Tool annotations are untrusted hints, not enforcement. | Read-only and write authorization are executor boundaries, not annotations. |

## Architecture

### System shape

```text
                                Clockify API
                                     │
                         HttpExecutor / AsyncClient
                                     │
                       permanent Operation registry
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
          ClockifyClient                           MCP adapters
                 │                                       │
        29 explicit resources                ┌────────────┴────────────┐
        reads and direct writes              │                         │
                                      ReadOnlyExecutor          ControlledWriteGate
                                              │                         │
                                      60 read tools +            approved exact plans
                                       5 workflows               only after milestone
```

Dependency direction is one way:

```text
models + operation definitions
            ↓
HTTP executor + response parsing
            ↓
SDK resources + ClockifyClient
            ↓
MCP read adapter
            ↓
MCP write adapter
```

The SDK never imports `clockify_mcp`. The transport never imports resources. Generated model files never import MCP code. MCP policy never leaks into normal SDK writes.

### Repository and package tree

```text
clockify-python/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── CHANGELOG.md
├── SECURITY.md
├── docs/
│   ├── architecture.md
│   ├── api-deviations.md
│   ├── mcp.md
│   ├── live-tests.md
│   └── port/
│       ├── MASTER_IMPLEMENTATION_PLAN.md
│       ├── OPERATION_PORT_MANIFEST.md
│       └── MCP_WRITE_SAFETY_PLAN.md
├── scripts/
│   └── import_openapi.py
├── src/
│   ├── clockify/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── config.py
│   │   ├── errors.py
│   │   ├── files.py
│   │   ├── money.py
│   │   ├── pagination.py
│   │   ├── raw.py
│   │   ├── response.py
│   │   ├── _transport/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── decode.py
│   │   │   ├── encode.py
│   │   │   ├── executor.py
│   │   │   ├── hosts.py
│   │   │   └── retry.py
│   │   ├── operations/
│   │   │   ├── __init__.py
│   │   │   ├── model.py
│   │   │   ├── registry.py
│   │   │   └── <29 domain modules>.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── <domain modules>.py
│   │   └── resources/
│   │       ├── __init__.py
│   │       ├── _base.py
│   │       └── <29 domain modules>.py
│   └── clockify_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── context.py
│       ├── errors.py
│       ├── result.py
│       ├── server.py
│       ├── read_executor.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── <read domain modules>.py
│       │   └── workflows.py
│       ├── workflows/
│       │   ├── doctor.py
│       │   ├── review.py
│       │   ├── status.py
│       │   └── workspace.py
│       └── writes/
│           ├── __init__.py
│           ├── executor.py
│           ├── gate.py
│           ├── nonce_store.py
│           ├── plan.py
│           ├── principal.py
│           ├── reconcile.py
│           └── state.py
├── tests/
│   ├── unit/
│   │   ├── transport/
│   │   ├── operations/
│   │   ├── resources/
│   │   └── models/
│   ├── contract/
│   │   ├── test_complete_surface.py
│   │   ├── test_public_method_wiring.py
│   │   └── test_known_deviations.py
│   ├── mcp/
│   │   ├── test_read_boundary.py
│   │   ├── test_read_tools.py
│   │   ├── test_workflows.py
│   │   ├── test_stdio.py
│   │   └── writes/
│   ├── importer/
│   ├── fixtures/
│   └── live/
└── .github/workflows/
    ├── ci.yml
    ├── live.yml
    └── release.yml
```

`<29 domain modules>` means the resource names fixed in `OPERATION_PORT_MANIFEST.md`. Do not collapse them into a single several-thousand-line module.

### Core contracts

#### Service and encoding types

```python
from dataclasses import dataclass
from enum import StrEnum


class Service(StrEnum):
    REGULAR = "regular"
    REPORTS = "reports"
    AUDIT_LOG = "audit_log"


class RequestEncoding(StrEnum):
    NONE = "none"
    JSON = "json"
    MULTIPART = "multipart"


class ResponseKind(StrEnum):
    JSON = "json"
    BYTES = "bytes"
    TEXT = "text"
    NONE = "none"
    CONTENT_NEGOTIATED = "content_negotiated"
```

These enums exist because the endpoint surface genuinely differs in these ways. Do not add generic media-type plugin machinery.

#### Query and pagination metadata

```python
@dataclass(frozen=True, slots=True)
class QueryParameter:
    python_name: str
    wire_name: str
    style: str = "form"
    explode: bool = True


@dataclass(frozen=True, slots=True)
class PaginationSpec:
    page_parameter: str
    page_size_parameter: str
    items_path: tuple[str, ...] | None
    count_path: tuple[str, ...] | None = None
    last_page_header: bool = False
```

The executor uses these records to serialize arrays correctly, map `page_size` to `page-size`, `pageSize`, or `size`, and extract list items from either a bare array or a proven envelope.

#### Mutation semantics

```python
class MutationEffect(StrEnum):
    NONE = "none"
    CREATE = "create"
    REPLACE = "replace"
    PATCH = "patch"
    TRANSITION = "transition"
    DELETE = "delete"
    BULK = "bulk"


class ReplacementSemantics(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    PATCH = "patch"
    FULL_REPLACE_PROVEN = "full_replace_proven"
    MIXED_PROVEN = "mixed_proven"
    UNKNOWN_CONSERVATIVE = "unknown_conservative"


@dataclass(frozen=True, slots=True)
class OperationSemantics:
    mutates: bool
    effect: MutationEffect
    replacement: ReplacementSemantics
    lifecycle: str | None = None
    replacement_required_fields: tuple[str, ...] = ()
```

`lifecycle` is a small closed vocabulary documented beside the constants, such as `archive_before_delete`, `done_before_delete`, or `pending_only`. It is not a free-form policy engine.

#### Permanent operation record

```python
@dataclass(frozen=True, slots=True)
class Operation:
    operation_id: str
    resource: str
    sdk_method: str
    http_method: str
    service: Service
    path: str
    path_parameters: tuple[str, ...]
    query_parameters: tuple[QueryParameter, ...]
    request_encoding: RequestEncoding
    response_kind: ResponseKind
    pagination: PaginationSpec | None
    semantics: OperationSemantics
```

Every field has an active consumer:

| Field | Consumer and reason |
|---|---|
| `operation_id` | stable registry key, raw SDK escape hatch, errors, tests, MCP binding |
| `resource`, `sdk_method` | unique public mapping and diagnostics |
| `http_method`, `service`, `path` | request construction and host routing |
| `path_parameters` | missing/extra path argument rejection before network |
| `query_parameters` | exact wire names and list serialization |
| `request_encoding` | JSON versus multipart versus no body |
| `response_kind` | JSON, bytes, text, empty, or content-negotiated decoding |
| `pagination` | page names, envelope extraction, and `Last-Page` handling |
| `semantics` | retry prohibition, read-only enforcement, replacement guards, and MCP preview behavior |

The runtime operation record deliberately does **not** include:

- authentication, because every supported operation follows the same exactly-one-credential client invariant;
- full request and response schemas, because static model classes own those contracts;
- documentation prose or evidence receipts, because product code does not need them;
- per-call data cache TTL, because the design has no Clockify response cache;
- MCP tool names, because MCP is an adapter and not every operation becomes a tool;
- risk labels that do not change runtime behavior.

### Operation registry

- Create one explicit `Operation` constant per endpoint.
- Split constants by the same 29 domains as the public resources.
- Build `ALL_OPERATIONS` in `operations/registry.py` through explicit imports and a tuple literal. Do not use decorators, import-time registration side effects, filesystem scanning, or `__subclasses__()`.
- Build `BY_ID` and `BY_PUBLIC_METHOD` once at import time. Raise immediately on a duplicate.
- The registry must assert 168 total, 62 non-mutating, 106 mutating, and 49 GET plus 13 POST reads in tests. Do not make package import fail because a count changed; the test is enough.
- The corrected OpenAPI is evidence used to construct the registry. It is not loaded at runtime and is not bundled in the wheel.

### Models and schemas

#### Decision

Use **Pydantic v2 static models**, generated once into readable committed Python source, with two small base classes:

```python
class ClockifyRequestModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )


class ClockifyResponseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )
```

This is a deliberate dependency, not a fashion choice:

- 339 reachable component-schema roots make handwritten runtime models a maintenance trap.
- aliases provide Python `snake_case` fields while preserving Clockify wire keys;
- request validation catches misspelled and missing replacement fields before destructive calls;
- response `extra="allow"` survives additive Clockify fields without discarding them;
- the same model types produce MCP input and elicitation schemas;
- validation errors are materially better than opaque server 400 responses;
- network cost dominates model-validation cost, and raw access remains available.

Do not add a second validation framework. Do not wrap every primitive in a custom class.

#### Model rules

1. Python attributes are `snake_case`; `Field(alias=...)` preserves exact wire spelling.
2. Request models forbid unknown fields. Response models preserve unknown fields in `model_extra`.
3. IDs remain strings. Do not globally require 24 hexadecimal characters because the evidence does not prove that for every identifier.
4. Date and timestamp fields remain strings or constrained string aliases. Do not automatically convert all values to `datetime`; Clockify evaluates some windows as wall-clock values in a supplied or account timezone.
5. Money remains in the exact operation’s wire unit. A field name or docstring must state `major_units`, `minor_units`, or `minor_times_100` where evidence proves it.
6. Use `Literal` for closed enums unless a named enum is reused in multiple domains and materially improves the API.
7. Use `RootModel` or `TypeAdapter` for root arrays and unions. Do not create empty wrapper classes only to satisfy a generator.
8. Request serialization uses aliases and preserves explicit `None` while excluding truly unset fields.
9. A replacement operation checks `replacement_required_fields` before sending. The operation-specific request model must also mark proven required fields as required.
10. Response parsing may be bypassed only through `client.raw`. Public resource methods return typed models, lists, pages, bytes, text, or `None`.

#### Small importer

`scripts/import_openapi.py` exists only to remove repetitive transcription from the 339 reachable schemas. It:

- accepts the corrected YAML path as an explicit command argument;
- verifies the expected source SHA when `--expect-sha256` is passed;
- emits deterministic model modules grouped by domain;
- handles local `$ref`, object, array, enum, `allOf`, `oneOf`, `anyOf`, nullable values, additional properties, binary fields, and aliases;
- emits a source SHA and “generated from corrected OpenAPI” header;
- refuses unsupported schema constructs with a precise path instead of emitting `Any` silently;
- never generates resource methods, MCP tools, workflows, safety logic, docs, CI, or release files;
- is tested against small fixtures, not against a second giant generated manifest.

The importer is a development tool. It is not a runtime dependency, does not run during installation, and has no routine drift/currentness gate. After the initial import, the repository must work from committed Python source alone.

### HTTP executor

#### Client reuse and ownership

`ClockifyClient` creates one `httpx.AsyncClient` by default and reuses it for every operation. It is an async context manager and has `aclose()`.

An advanced caller may inject an existing `httpx.AsyncClient`. When injected, the SDK does not close it. This ownership rule is explicit and tested.

#### Authentication invariant

Construction accepts exactly one of:

- `api_key`, sent as `X-Api-Key`; or
- `addon_token`, sent as `X-Addon-Token`.

Both or neither raise `ClockifyConfigurationError` before any request. Secrets never appear in `repr`, errors, logs, or MCP output.

#### Host routing

Default service URLs are fixed:

```text
REGULAR   → https://api.clockify.me/api/v1
REPORTS   → https://reports.api.clockify.me/v1
AUDIT_LOG → https://auditlog-api.api.clockify.me/v1
```

Only these global routes are proven. Do not port the TypeScript region/subdomain matrix into v1.

Custom service URLs are allowed only when the caller passes an explicit `allow_custom_hosts=True`. Before adding an authentication header, the executor validates the final URL against the selected service URL. Redirect following is disabled. A 3xx response is returned as an error; credentials are never followed to another host.

#### Request construction order

For every call:

1. resolve the operation by ID or constant;
2. resolve explicit or default workspace ID;
3. validate exact path arguments;
4. render the path with percent-encoded values;
5. map Python query names to wire names and serialize according to `style`/`explode`;
6. serialize a request model using aliases, or prepare multipart fields/files;
7. combine default and caller headers, with caller values winning;
8. validate the destination host;
9. attach exactly one Clockify credential;
10. dispatch through the reused `AsyncClient`;
11. treat any 2xx status as success and decode according to `response_kind` and actual content type;
12. normalize non-2xx failures into the SDK error hierarchy.

Default headers:

- a package `User-Agent`, unless the caller supplied one;
- a generated UUID `X-Request-Id`, unless the caller supplied one.

#### Timeouts and cancellation

Use an explicit `httpx.Timeout` with separate connect, read, write, and pool values. Defaults should be sane for an API client, not tuned to a microbenchmark. A caller can replace the timeout globally or per call.

Do not catch `asyncio.CancelledError`. Closing the task must cancel the in-flight HTTP request. MCP cancellation propagates to the same executor.

#### Retry policy

The default is no retry. An optional small `ReadRetryPolicy` may be enabled. It is enforced at the final executor boundary:

- only `operation.semantics.mutates is False` can be retried;
- this includes the 13 read `POST` operations;
- retryable conditions are connection failures and `408`, `429`, `500`, `502`, `503`, and `504`;
- honor a valid `Retry-After` value;
- use a bounded attempt count and capped exponential delay with jitter;
- cancellation stops immediately;
- a mutating operation is attempted once even if the caller configured a read retry policy.

Do not implement mutation retries, idempotency-key injection, retry plugins, queues, or background replay.

#### Response decoding

- `JSON`: decode JSON, then validate through the resource method’s Pydantic adapter. An empty successful body becomes `None` only when the operation contract allows no content.
- `BYTES`: return `BinaryResponse` containing bytes, content type, filename when present, status, headers, and request ID.
- `TEXT`: return decoded text using the response charset, defaulting safely to UTF-8.
- `NONE`: consume/close the response and return `None`.
- `CONTENT_NEGOTIATED`: inspect actual `Content-Type`; select JSON, text/CSV, or bytes. Unknown binary content remains bytes, never lossy text.

No decoder silently replaces invalid binary bytes with Unicode replacement characters.

### Public client and resources

```python
async with ClockifyClient(
    api_key=os.environ["CLOCKIFY_API_KEY"],
    workspace_id=os.getenv("CLOCKIFY_WORKSPACE_ID"),
) as clockify:
    page = await clockify.projects.list(archived=False)
    project = await clockify.projects.get("project_id")
    created = await clockify.projects.create(ProjectCreateRequest(name="Example"))
```

Rules:

- `workspace_id` on the client is optional. A workspace-scoped method accepts a keyword override. If neither exists, it raises before network.
- Resource objects are constructed once and exposed as typed attributes on `ClockifyClient`.
- Every operation has one explicit method. No `__getattr__`, runtime method generation, dynamic descriptors, generic CRUD superclass, or stringly typed primary API.
- Path identifiers are explicit parameters. Query parameters are keyword-only and use Python names.
- Body operations accept their generated request model or a mapping that is validated into that model.
- Resource methods return typed response models, `list[T]`, `Page[T]`, `BinaryResponse`, `str`, or `None`.
- Method docstrings state lifecycle prerequisites, replacement risk, and non-obvious units. They do not reproduce the whole OpenAPI description.

`resources/_base.py` may contain only concrete shared call plumbing: workspace resolution, request-model coercion, and response adaptation. It must not contain generic CRUD semantics.

#### Raw escape hatch

`client.raw.call(operation_id, *, path, query, body, files, headers)` is a secondary API for advanced consumers. It:

- accepts only registered operation IDs;
- uses the same auth, host, encoding, retry, and error boundaries;
- returns `ClockifyResponse[Any]` without model adaptation;
- cannot target an arbitrary URL;
- remains subject to `ReadOnlyExecutor` when used by MCP.

Ugly OpenAPI operation IDs therefore remain available without becoming the public SDK’s main interface.

### Errors

Use a small hierarchy:

```text
ClockifyError
├── ClockifyConfigurationError
├── ClockifyTransportError
│   └── MutationOutcomeUnknownError
├── ClockifyResponseValidationError
├── ClockifyReadOnlyViolation
├── ClockifyLifecycleError
└── ClockifyAPIError
    ├── ClockifyAuthenticationError
    ├── ClockifyPermissionError
    ├── ClockifyNotFoundError
    ├── ClockifyConflictError
    └── ClockifyRateLimitError
```

`ClockifyAPIError` carries:

- operation ID;
- status code;
- parsed upstream message/body when safe;
- Clockify numeric or string body code without assuming one type;
- request ID;
- retry-after value where present;
- response headers needed for diagnosis.

Do not create one exception class for every HTTP status or every historical message. Preserve the upstream detail and expose stable broad categories.

Any transport failure during a mutation becomes `MutationOutcomeUnknownError`, because the client cannot prove whether Clockify applied the request. The error tells the caller to read back state before retrying.

### Pagination

`Page[T]` is a frozen dataclass with:

- `items`;
- requested page and page size;
- `last_page: bool | None`;
- optional count;
- request ID and relevant response headers.

`iter_pages(fetch_page, ...)` and `iter_all(fetch_page, ...)` are free functions. A resource method remains an ordinary page fetcher; no hidden iterator protocol is added to every resource.

Stop rules, in order:

1. empty page always stops;
2. valid `Last-Page: true` stops;
3. valid `Last-Page: false` continues even after a short page;
4. without a valid header, a short page stops;
5. an exact repeated non-empty page stops with `PaginationLoopError`;
6. `max_pages` stops with an explicit incomplete-result error, never a silently truncated list.

### Files and multipart

`Upload` is a small dataclass:

```python
@dataclass(slots=True)
class Upload:
    filename: str
    content: bytes | BinaryIO
    content_type: str = "application/octet-stream"
```

The SDK never closes caller-owned file objects. Multipart encoding handles only the three proven endpoints: image upload and expense create/update. Do not add a generic multipart framework.

`BinaryResponse.save(path)` may be a convenience method. It writes bytes exactly and does not infer text.

### Corrected Clockify behavior

Port the behavior, not the proof machinery. At minimum, focused tests must cover these classes of correction:

- the three service hosts;
- body-based POST reads;
- `Last-Page` and per-operation page parameter names;
- bare array versus envelope extraction;
- invoice/payment/expense/invoice-item money scales;
- archive/DONE-before-delete rules;
- pending-only time-off withdrawal;
- balance-assignment create/update delta behavior;
- invoice payment create returning an invoice rather than the payment ID;
- full-replacement and mixed-omission behavior for clients, projects, tags, holidays, policies, invoices, and other proven operations;
- client update preserving `ccEmails`;
- tag update preserving `archived`;
- exact seven-day weekly reports;
- wall-clock date-range semantics;
- absent single-get routes and list-based fallback;
- binary receipt/export handling;
- shared-report public view returning rendered report content;
- unsupported/no-op idempotency key behavior;
- operation-specific status/body deviations recorded in the manifest.

A discrepancy correction should normally be one implementation change plus one regression test. Do not add an evidence ledger, source-currentness timestamp, policy file, generated receipt, and validator for the same fact.

### Read MCP architecture

#### Server

Use official `mcp` v2 and `MCPServer`. The stdio entry point is:

```bash
clockify-mcp
# equivalent
python -m clockify_mcp
```

Stdout is reserved for MCP protocol traffic. Logs go to stderr. Server construction performs no Clockify request.

#### Restricted context

```text
MCP tool/workflow
      │
      ▼
ClockifyClient built over ReadOnlyExecutor
      │
      ▼
ReadOnlyExecutor.execute(operation, ...)
      │
      ├── operation.mutates == True  → ClockifyReadOnlyViolation
      └── operation.mutates == False → HttpExecutor.execute(...)
```

The MCP context receives only the restricted client. It does not receive the normal `HttpExecutor`. Raw calls use the same restricted executor.

Defense in depth is limited to two cheap checks:

1. registration tests assert every raw read tool maps to a non-mutating operation;
2. the final execution boundary rejects any mutating operation regardless of registration metadata.

`readOnlyHint` is set correctly but is never treated as the boundary.

#### Raw read tools

Register the 60 eligible operations as explicit tool functions grouped by domain. Tool names follow:

```text
clockify_<resource>_<method>
```

Examples:

```text
clockify_projects_list
clockify_time_entries_get_many
clockify_reports_summary
clockify_webhooks_search_logs
```

Each tool:

- has a typed, useful input schema from explicit parameters and request models;
- returns a structured read result with `data`, operation ID, request ID, pagination metadata, and warnings;
- uses `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, and `openWorldHint=true`;
- does not cache Clockify data;
- does not expose receipt download or invoice export binary bytes;
- limits shared-report public view to JSON/CSV and rejects PDF/XLSX before network.

Do not generate tool functions at runtime from the registry. Repetition is acceptable when it keeps schemas, names, and behavior obvious.

#### Read workflows

Only these ship initially:

1. `clockify_status` — current user, configured/default workspace, and running timers.
2. `clockify_workspace_overview` — workspace identity plus concise counts/summaries of users, projects, tags, and relevant settings.
3. `clockify_review_day` — a user’s entries for one explicit day and timezone, with optional project/task correlation.
4. `clockify_review_week` — an exact seven-day interval with entries and report summary.
5. `clockify_doctor` — credential/configuration diagnosis and minimal read connectivity checks; no writes.

Every workflow receives the restricted client and uses ordinary resource methods. Do not create workflows merely to hide the raw tool count. Do not port repository-governance tools such as docs search, operation guides, SDK snippets, release planners, or demo-data management.

### MCP write architecture

The write design is fully specified in `MCP_WRITE_SAFETY_PLAN.md`. The load-bearing choices are:

- confirmation is a model-invisible `Resolve(Elicit(...))` dependency;
- on protocol `2026-07-28`, the official SDK carries it as MRTR and seals `requestState`;
- on legacy protocol, the same resolver uses the supported synchronous elicitation path;
- a deterministic exact preview is built from validated arguments and current Clockify state;
- a bounded in-memory nonce store gives atomic, true single-use semantics;
- a consumed execution permit binds the exact ordered HTTP plan;
- the final controlled executor refuses any operation or serialized arguments not present in that permit;
- the nonce is consumed before the first mutation dispatch;
- writes are never automatically retried;
- ambiguous network outcomes are reported as unknown and require read-back;
- multi-step lifecycle plans report partial completion exactly.

No MCP write tool is registered during the read-MCP phases.

### Packaging and developer experience

#### Naming

- Repository: `clockify-python`
- Distribution: `clockify-python-115`
- SDK import: `clockify`
- MCP import: `clockify_mcp`
- Console script: `clockify-mcp`

The `-115` distribution suffix preserves the existing unofficial-project distance. The import remains concise and conventional.

#### Python and build

- Minimum Python: **3.11**.
- Build backend: `hatchling` through PEP 517/621.
- Environment and lock management: `uv`.
- Version source: one static package version in `pyproject.toml` until automation is justified.
- Semantic versioning.
- One wheel contains both import packages; MCP dependencies are optional through `[mcp]`.

Typical installation:

```bash
uv add clockify-python-115
uv add "clockify-python-115[mcp]"
```

#### Public exports

`clockify.__init__` exports only the primary client, configuration, public models/types intended for direct use, pagination helpers, file helpers, and public errors. Internal transport and operation implementation modules stay importable for tests but are not documented as stable.

`clockify_mcp` exposes server construction for embedding and the console entry point. It does not re-export the entire SDK.

## Dependency audit

| Dependency | Scope | Concrete job | Why the standard library is insufficient | Decision |
|---|---|---|---|---|
| `httpx` | core runtime | async connection pooling, timeouts, multipart, TLS, mock transport | stdlib has no comparable async HTTP client | required |
| `pydantic` v2 | core runtime | aliases, complete request/response models, validation, MCP-compatible schemas | handwritten validation/alias conversion across 339 schema roots would be larger and worse | required |
| `mcp` v2 | optional MCP runtime | protocol, `MCPServer`, MRTR, elicitation, request-state security, stdio | implementing MCP is out of scope and unsafe | optional extra |
| `hatchling` | build | standard wheel/sdist production | a build backend is required | build dependency |
| `pytest` | development | deterministic tests | stdlib `unittest` has weaker async/fixture ergonomics for this project | dev only |
| `pytest-asyncio` | development | explicit async test execution | avoids custom loop fixtures | dev only |
| `ruff` | development | lint and format | replaces several tools with one fast tool | dev only |
| `pyright` | development | strict static type checking | runtime tests do not prove type contracts | dev only |
| `PyYAML` | importer development | read corrected YAML | stdlib does not parse YAML | dev/importer only |

Do not add `orjson`, `tenacity`, `datamodel-code-generator`, `jsonschema`, a DI framework, a cache, a database, Redis, telemetry SDKs, or a CLI framework in the initial repository. Add a dependency only when a concrete accepted requirement cannot be met more simply.

## Implementation sequence

### Phase 0 — Freeze evidence and prove uncertain framework seams

**Objective:** remove the remaining architectural uncertainty before product code expands.

**Files:**

- copy the three planning artifacts into `docs/port/`;
- create a temporary `spikes/` directory that is deleted before Phase 1 completes;
- no production package yet.

**Exact work:**

1. Verify the corrected OpenAPI SHA and the 168/62/106/49/13 counts independently.
2. Verify all 168 proposed `(resource, method)` pairs are unique and no method is a Python keyword.
3. Build a minimal Pydantic prototype for representative alias, union, root-array, additional-property, multipart, and response-extra schemas.
4. Build a minimal official MCP v2 prototype that proves:
   - `MCPServer` tool schema generation from the chosen model style;
   - `Resolve(Elicit(...))` over an in-memory 2026-07-28 client;
   - the same resolver under a forced legacy protocol;
   - custom `RequestStateSecurity.bind_principal` construction;
   - repeated `requestState` can pass integrity checks and therefore still needs server-side nonce consumption;
   - real stdio keeps stdout clean.
5. Delete the spikes after recording the resulting implementation decisions in these plans if any assumption changes.

**Invariants:** no Clockify live mutation; no repository implementation is started on an unproven MCP interaction assumption.

**Tests/acceptance:** executable spike tests pass; every changed assumption is integrated into the plans, not appended as contradictory notes.

**Must not build:** a prototype architecture that remains in production, a second operation inventory, or any write tool.

### Phase 1 — Create the minimal repository skeleton

**Objective:** make clone/install/test/build boring before API code lands.

**Files:** `pyproject.toml`, package directories, test directories, `README.md`, `LICENSE`, `SECURITY.md`, `.gitignore`, `ci.yml`.

**Exact behavior:**

- configure Python 3.11+, hatchling, uv, ruff, pyright, pytest;
- define core and `mcp` optional dependencies;
- add empty importable `clockify` and `clockify_mcp` packages;
- add the `clockify-mcp` entry point, which may print only a clear “server not built” error to stderr until the read-MCP phase;
- configure strict but practical pyright settings and ruff defaults without dozens of project-specific ignores;
- build wheel and sdist.

**Acceptance:** clean virtual environment can `uv sync`, import both packages, run empty tests, and `uv build`.

**Must not build:** pre-commit framework, Makefile with target aliases, custom task runner, release ceremony, code coverage policy, mutation testing, or docs-count gates.

### Phase 2 — Implement models and the permanent operation registry

**Objective:** establish the static contracts used by every later phase.

**Files:** `models/**`, `operations/**`, `scripts/import_openapi.py`, importer/operation tests.

**Exact behavior:**

- implement model base classes and deterministic importer;
- generate and review all 339 reachable component-schema roots and all required inline schemas;
- hand-author the 168 operation records from `OPERATION_PORT_MANIFEST.md`, split into 29 modules;
- include exact path/query names, request/response kinds, pagination, semantic mutation status, replacement risk, and lifecycle requirements;
- create explicit `ALL_OPERATIONS`, `BY_ID`, and public-method maps;
- preserve the six unreachable component schemas as excluded, documented evidence rather than generating dead code.

**Edge cases:** nested `$ref` to `SharedReportCreate/properties/type` is not a component-schema root; aliases with acronyms; nullable unions; root arrays; arbitrary response extras; binary schema fields; schemas used by multiple domains.

**Tests:**

- importer fixture/golden tests for supported constructs and fail-closed unsupported constructs;
- all generated modules import and `model_rebuild()` succeeds;
- 168 unique operation IDs and public mappings;
- exact 62/106 and 49/13 classifications;
- exact three-service routing counts 157/10/1;
- exactly three multipart operations;
- no request model silently accepts an unknown field;
- response models preserve an unknown field.

**Acceptance:** the complete static surface imports with no HTTP code and no `Any` introduced merely because the importer did not understand a schema.

**Must not build:** runtime OpenAPI loading, generated public methods, generated MCP tools, schema-currentness CI, or a general OpenAPI framework.

### Phase 3 — Implement the HTTP foundation

**Objective:** one small executor correctly reaches every Clockify service and response class.

**Files:** `_transport/**`, `config.py`, `errors.py`, `response.py`, `files.py`, `raw.py`.

**Exact behavior:** implement auth, service routing, URL rendering, query encoding, JSON and multipart encoding, header precedence, request IDs, explicit timeout, optional read-only retries, response decoding, error normalization, raw registry calls, and ownership/close semantics.

**Invariants:**

- credentials are attached only after final-host validation;
- redirects are not followed;
- writes are never retried;
- caller headers win;
- every response is closed;
- cancellation propagates;
- a mutation transport failure is reported as outcome unknown.

**Tests:** `httpx.MockTransport` cases for all request/response classes, service hosts, custom-host opt-in, redirect rejection, auth exclusivity, query list styles, body null versus omitted, multipart files, JSON/text/bytes/empty/content-negotiated responses, error bodies, request IDs, timeout, cancellation, and retry boundary including a read `POST` and a write `GET`-heuristic trap.

**Acceptance:** table-driven executor tests cover every operation metadata combination present in the 168 records.

**Must not build:** cache, write retry, arbitrary URL request method, background queue, synchronous client, or observability framework.

### Phase 4 — Implement all 168 explicit SDK methods

**Objective:** complete the public Python SDK surface.

**Files:** `client.py`, `resources/_base.py`, 29 resource modules, public exports, resource tests.

**Exact behavior:**

- expose all 29 resource properties;
- implement each unique method from the manifest;
- use optional default workspace plus keyword override;
- validate request mappings into Pydantic models;
- pass exact path/query/body/files to the executor;
- adapt raw JSON to the declared response model/page/list;
- write concise docstrings for non-obvious semantics.

**Implementation batching:** domains may be implemented in waves, but a wave is not declared complete until every operation assigned to it has a public-method request-construction test.

**Tests:** a 168-case public wiring suite calls every method against `MockTransport` and asserts operation ID, method, host, rendered path, query, body encoding, and response adapter. This fixture drives the public method; it is not a test that one generated manifest equals another.

**Acceptance:** `OPERATION_PORT_MANIFEST.md` has no operation without a callable resource method and no callable method without an operation record.

**Must not build:** magic method generation, generic CRUD methods, a sync facade, CLI, or convenience helpers whose behavior is not yet proven.

### Phase 5 — Encode corrected behavior and high-value SDK helpers

**Objective:** turn accumulated Clockify knowledge into ordinary correct behavior.

**Files:** focused resource/helper changes, `money.py`, `pagination.py`, deviation tests, user docs.

**Exact behavior:**

- implement `Page`, `iter_pages`, and `iter_all`;
- implement exact unit-named money helpers;
- implement proven list-based single-get fallbacks where no route exists;
- enforce replacement-required fields and documented lifecycle prerequisites;
- add small semantic helpers only where they remove a proven data-loss trap, such as safe archive/update or archive-then-delete flows;
- ensure helpers state their multiple HTTP steps and never hide partial failure;
- preserve current client CC emails, tag archive state, and other proven fields during safe read-modify-write helpers;
- correctly recover or explicitly fail to recover a created payment ID;
- handle binary receipt/export and shared-report media types exactly.

**Edge cases:** changed state between read and replace; no single GET; deleted project returning 400; empty lists; weird `Last-Page`; exact weekly interval; account/report timezone; explicit empty arrays used to clear values; expense major-unit input versus minor-unit response.

**Tests:** one focused regression test per retained discrepancy class, with descriptive names that state the real failure mode.

**Acceptance:** every “Corrected behavior” entry in the operation manifest is either represented by code/docstring/test or explicitly marked unresolved without invented behavior.

**Must not build:** an evidence ledger, live-evidence freshness gate, broad policy system, or automatic cleanup that can hide a failed primary operation.

### Phase 6 — Ship the structural read MCP

**Objective:** deliver useful MCP reads with a hard non-mutation boundary.

**Files:** `clockify_mcp/server.py`, context/result/error modules, `read_executor.py`, domain read tool modules, MCP tests, stdio entry point.

**Exact behavior:**

- construct `MCPServer` from environment/config without network;
- build the SDK resource client over `ReadOnlyExecutor`;
- register all 60 eligible raw read tools explicitly and deterministically;
- omit binary-only receipt and invoice export operations;
- limit public shared-report view to JSON/CSV;
- convert SDK errors to safe, actionable tool errors;
- return request IDs and pagination metadata;
- set accurate annotations, including `openWorldHint=true` for Clockify-backed tools;
- send logs only to stderr.

**Invariants:** no read tool or workflow receives a normal executor; the final boundary rejects `mutates=True`; no MCP write tool is registered.

**Tests:**

- all advertised raw tools map to non-mutating operations;
- all 60 eligible operations are exposed exactly once;
- a deliberately miswired workflow write attempt is blocked before mock HTTP sees a request;
- in-memory client tests exercise representative GET and POST reads;
- a spawned stdio client lists tools and calls one tool with stdout protocol integrity;
- missing credentials produce a setup error without leaking values.

**Acceptance:** read MCP is independently publishable and useful while write modules remain unimported.

**Must not build:** tool discovery bureaucracy, repository docs-search tools, response caching, write preview, or confirmation tokens.

### Phase 7 — Add the five read workflows

**Objective:** add only workflows that solve a clear agent job better than one raw operation.

**Files:** workflow modules and tests.

**Exact behavior:** status, workspace overview, day review, week review, and doctor as defined above. Each workflow uses bounded pagination, explicit timezones/windows, concise results, and the restricted client.

**Tests:** composition call order, pagination, empty states, exact seven-day rules, timezone input, cancellation, and deliberate attempted mutation rejection.

**Acceptance:** each workflow has a documented user job and at least one end-to-end in-memory MCP test. Removing the workflow would make that job materially harder, not merely reduce tool count.

**Must not build:** demo seed/cleanup, write workflows, generic plan runners, or model-generated summaries that conceal raw data.

### Phase 8 — Build and prove the write-safety core without exposing writes

**Objective:** implement the reusable safety boundary in isolation.

**Files:** `clockify_mcp/writes/**` and adversarial tests. No write tool registration.

**Exact behavior:** implement validated `WritePlan`, deterministic preview rendering, model-invisible approval dependency, custom request-state principal binding, bounded atomic nonce store, exact execution permits, controlled ordered-step executor, expiry, cancellation, preconditions, outcome-unknown handling, partial-failure receipts, and reconciliation.

**Tests:** every adversarial case in `MCP_WRITE_SAFETY_PLAN.md`, including tampering, replay, concurrent consumption, state drift, process restart, identical concurrent calls, legacy and modern protocol modes, cancellation at each boundary, and mismatch between approved and dispatched bytes.

**Acceptance:** an independent reviewer can demonstrate that no mutation reaches mock HTTP without one valid unconsumed exact-plan permit, and that one permit cannot dispatch twice.

**Must not build:** any registered write tool, distributed store, durable queue, risk bureaucracy, or automatic retry.

### Phase 9 — Add MCP writes in behavior-based waves

**Objective:** expose useful writes only through the proven gate.

**Wave order:**

1. single-entity additive or reversible writes with direct read-back;
2. status transitions and partial updates;
3. full/mixed replacement operations with precondition fingerprints;
4. lifecycle multi-step delete operations;
5. financial, access-control, time-entitlement, external-delivery, and bulk operations;
6. file-bearing writes only after exact byte hashing, preview, size limits, and target-client support are proven.

This is not a “risk level” taxonomy. The waves exist because later groups require additional concrete behavior.

**For each write tool:**

- explicit typed function;
- exact underlying operation(s);
- deterministic preview;
- operation/args/principal/workspace/nonce binding;
- read-back or explicit lack of read-back;
- partial/unknown outcome handling;
- focused adversarial tests;
- target-host UI compatibility evidence.

**Acceptance:** only the individually reviewed tools are registered. The existence of an SDK write method never automatically exposes an MCP tool.

**Must not build:** all 106 tools in one mechanical batch, blanket `LOW` approval bypass, write annotations as enforcement, or a generic “call any operation” MCP write tool.

### Phase 10 — Finish packaging, documentation, and release proof

**Objective:** prove the installable artifact, not repository ceremony.

**Files:** README, architecture/deviation/MCP/live docs, examples, release workflow, changelog.

**Exact behavior:**

- SDK quickstart, pagination, multipart, errors, raw access, and replacement/lifecycle examples;
- MCP stdio configuration and read/write support statement;
- package build and clean-venv wheel install;
- import and console-script smoke;
- semantic version/changelog update;
- publish only through explicit release workflow with trusted publishing when configured.

**Acceptance:** a fresh clean environment installs the built wheel, runs an SDK mock example, starts MCP over stdio, and passes the non-live suite.

**Must not build:** release-please mirror files, pack snapshots, release receipts, generated docs-count contracts, or dozens of release gates.

## Maintenance model

### Add an endpoint

1. Reconcile the endpoint against the current corrected source and real behavior.
2. Add the exact operation record in the appropriate domain module.
3. Add or regenerate only the needed request/response models.
4. Add one explicit resource method.
5. Add one public-method request-construction test and any behavior-specific test.
6. Add a read tool only when the operation is verified non-mutating and useful to agents.
7. Add a write tool only through the write-safety workflow below.

Normal target: **three or four product files plus tests**. If the change needs ten unrelated files, stop and question the architecture.

### Fix an API discrepancy

1. Reproduce or locate reliable evidence.
2. Identify whether the defect is transport metadata, schema/model, resource semantics, or a helper.
3. Fix the narrowest correct boundary.
4. Add a regression test named after the user-visible failure.
5. Update `docs/api-deviations.md` in one concise entry when users need to know it.

Do not create a policy, manifest, currentness timestamp, and generator override for one behavior.

### Add an MCP read tool

1. Confirm `operation.semantics.mutates is False` from behavior, not verb.
2. Add an explicit tool function and useful schema/description.
3. Map it to the existing resource method through the restricted client.
4. Add registration and in-memory call tests.
5. Keep the executor-boundary rejection test green.

### Add a read workflow

1. State the user job and why raw tools are materially worse.
2. Compose only existing read resource methods.
3. Accept explicit scope, timezone, pagination, and output limits.
4. Test empty, partial, and cancellation behavior.
5. Do not bypass `ReadOnlyExecutor` for convenience.

### Add an MCP write safely

1. Classify concrete effect, scope, sensitivity, replacement semantics, lifecycle steps, read-back ability, and ambiguity behavior.
2. Build the exact `WritePlan` from validated arguments and current state.
3. Add deterministic preview and precondition fingerprint.
4. Route approval through the shared resolver and nonce store.
5. Route execution through an exact permit and controlled executor.
6. Add replay, concurrent-use, drift, cancellation, partial-failure, and outcome-unknown tests.
7. Run target-client compatibility tests.
8. Register the tool only after independent review passes.

## Quality gates

### Local development

Required before a focused commit:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q -m "not live"
```

During active work, run the smallest relevant test file first. The full non-live suite must remain fast enough to run routinely.

### Pull request

One CI workflow runs:

1. dependency install from lock;
2. ruff check and format check;
3. pyright;
4. full non-live pytest suite;
5. `uv build`;
6. clean-environment wheel install and import/console smoke;
7. tests on the minimum Python and one current newer Python version.

No routine live Clockify calls. No mutation testing. No generated-doc drift suite.

### Release

A release requires:

- all PR gates on the release commit;
- changelog and version update;
- wheel/sdist build;
- clean install and smoke from the exact artifacts;
- MCP stdio smoke from the wheel;
- dependency vulnerability review appropriate to the release, without a custom policy engine;
- manual publish authorization.

For a release that adds MCP writes, it also requires the write-safety ship conditions and target-client compatibility evidence.

### Optional live verification

A manual `live.yml` workflow may run against a sacrificial workspace only. It is separate from ordinary CI.

- Read tests can run broadly.
- Mutation tests create uniquely prefixed entities, capture returned IDs, and clean them explicitly.
- A test must report cleanup failure; it must not claim green while residue remains.
- No customer workspace is permitted.
- A live result supports a specific behavior claim; it does not become a general currentness gate for every commit.

## Definition of done

### SDK

- [ ] One installable distribution and one async `ClockifyClient`.
- [ ] Exactly 168 registered operations and 168 explicit public methods.
- [ ] Exactly 29 resource attributes with no method-name collision.
- [ ] Exactly 62 non-mutating and 106 mutating operations; 49 GET reads and 13 POST reads.
- [ ] Three-host routing, auth, host validation, timeout, cancellation, and header precedence are proven.
- [ ] JSON, multipart, binary, text, content-negotiated, and no-content responses are proven.
- [ ] All reachable schemas needed by the surface have reviewed static models.
- [ ] Pagination and all retained API deviations have focused tests.
- [ ] No write auto-retry and no false idempotency claim.
- [ ] Wheel install smoke passes from a clean environment.

### Read MCP

- [ ] 60 raw read tools are exposed exactly once.
- [ ] Two binary-only reads remain SDK-only; shared-report binary formats are rejected before network.
- [ ] Five curated read workflows are implemented and tested.
- [ ] Every path uses `ReadOnlyExecutor` and a deliberate write attempt is blocked before HTTP.
- [ ] Tool annotations are accurate and not used as enforcement.
- [ ] In-memory and real stdio tests pass.

### Write MCP

- [ ] No write is exposed merely because it exists in the SDK.
- [ ] All invariants and adversarial tests in `MCP_WRITE_SAFETY_PLAN.md` pass.
- [ ] Exact preview, request-state protection, principal binding, atomic single-use, expiry, concurrency, state drift, retries, lifecycle, partial failure, and ambiguous outcomes are proven.
- [ ] Target clients show the exact approval UI and fail closed when elicitation is unsupported.
- [ ] An independent reviewer approves the safety boundary before the first write tool ships.

### Maintainability and governance

- [ ] Adding an ordinary endpoint follows the four-step maintenance model without hidden registration.
- [ ] No runtime metaprogramming, dynamic public methods, generic CRUD framework, or import side effects.
- [ ] No giant generator pipeline, live-evidence currentness system, duplicated manifests, docs-count checks, mutation-test requirement, or 100-target task runner.
- [ ] Tests prove product behavior rather than the existence of other checks.
- [ ] Repository names and module boundaries let a human or coding agent locate behavior without chat history.

## Integrated adversarial review

The final architecture was reduced after challenging the initial direction:

- **Rejected:** copying the TypeScript generated SDK plus wrapper boundary. **Reason:** Python can keep explicit resources and a much smaller schema importer without a second generated client layer.
- **Rejected:** one huge `operations.py`. **Reason:** 168 rich records plus semantics would become a maintenance hotspot. Domain modules with one explicit registry keep locality.
- **Rejected:** TypedDict-only request/response handling. **Reason:** Pythonic aliases, replacement validation, response parsing, and MCP schema production would otherwise require a second custom conversion/validation system. Pydantic has a concrete job here.
- **Rejected:** Pydantic strict response rejection. **Reason:** Clockify adds and varies fields. Response models allow extras; raw access exists.
- **Rejected:** verb-derived read/write classification. **Reason:** it loses 13 real reads.
- **Rejected:** `readOnlyHint` as security. **Reason:** annotations are untrusted hints.
- **Rejected:** direct manual MRTR as the normal confirmation path. **Reason:** official `Resolve(Elicit(...))` supplies the same modern MRTR path and legacy compatibility while keeping approval invisible to the model. Manual `InputRequiredResult` remains a low-level mechanism, not the product architecture.
- **Rejected:** sealed `requestState` as single-use proof. **Reason:** integrity, expiry, request, principal, and audience binding do not atomically consume state. A bounded nonce store remains necessary.
- **Rejected:** distributed confirmation infrastructure for stdio. **Reason:** process-local key plus process-local atomic store is the correct scope. A remote multi-worker product would be a new deployment decision.
- **Rejected:** broad risk levels. **Reason:** only concrete dimensions that change preview, precondition, bulk limit, or execution behavior remain.
- **Rejected:** automatic safe-update behavior inside every raw `update`. **Reason:** omission semantics differ and some are unresolved. Raw methods stay explicit; only evidence-backed safe helpers compose reads and writes.
- **Rejected:** routine live and mutation proof. **Reason:** deterministic mock/contract tests cover the normal loop; live proof is manual and claim-specific.

The result is intentionally boring: one executor, one operation record per endpoint, one explicit resource method per operation, one hard read boundary, and one independently proven write gate.

## IMPLEMENTER CONTRACT

The implementation model must follow this section even when it would choose a different framework or abstraction in a fresh project.

### Decisions that MUST be preserved

1. One repository and distribution with `clockify` and `clockify_mcp` import packages.
2. Python 3.11+, async-first SDK, one reused `httpx.AsyncClient`.
3. All 168 operations and the exact resource/method mappings in `OPERATION_PORT_MANIFEST.md`.
4. Semantic counts: 62 reads, 106 writes, 49 GET reads, 13 POST reads.
5. Explicit resource methods and explicit MCP tool functions. No runtime public-method/tool generation.
6. Permanent operation records with exact routing, encoding, pagination, and mutation semantics.
7. Pydantic v2 static models with Python aliases; request extras forbidden and response extras allowed.
8. Exactly-one Clockify credential, final-host validation before auth, redirects disabled, caller headers preserved.
9. No automatic mutation retry and no idempotency-key safety claim.
10. Final-boundary `ReadOnlyExecutor` for every read MCP path.
11. MCP write safety remains absent until the companion safety plan is independently proven.
12. MCP confirmation uses official resolver/elicitation behavior, sealed request state on modern protocol, and an atomic server-side nonce store.
13. Product behavior is proved with focused tests; TypeScript governance machinery is not ported.

### Freedoms the implementer DOES have

- choose exact internal helper names when the responsibility remains obvious;
- split a large domain model or test file further;
- improve type precision when evidence supports it;
- choose sensible timeout and bounded retry numeric defaults and document them;
- improve docstrings and examples without changing behavior;
- remove an abstraction that becomes unnecessary while preserving all invariants;
- use a more direct implementation when it reduces code and keeps the same tests and contracts.

### Forbidden shortcuts

- omitting an operation because it is obscure;
- classifying reads by verb;
- using OpenAPI operation IDs as the primary public API;
- returning untyped `dict[str, Any]` from every resource method;
- using `__getattr__`, decorators with registration side effects, reflection scans, monkeypatching, or dynamic CRUD generation;
- bypassing final host validation or following authenticated redirects;
- retrying a write, including `PUT` or `DELETE`, automatically;
- assuming every PUT is full replacement or partial update;
- using annotations, descriptions, or approval prose as the safety boundary;
- exposing a generic raw MCP mutation tool;
- translating the TypeScript `ConfirmationTokenStore` line by line;
- building Redis, a database, a queue, or distributed locks for local stdio;
- recreating large policy/manifest/currentness/release-gate systems;
- claiming a gate or endpoint complete when its required test has not run.

### Required tests

- registry counts, uniqueness, service routing, multipart count, and semantic read/write classification;
- request construction through every one of the 168 public methods;
- every transport/response kind and pagination style;
- every retained known deviation class;
- auth/host/header/retry/cancellation/error contracts;
- all 60 read tools and the final read-only rejection boundary;
- five workflow behaviors;
- real stdio protocol smoke;
- every adversarial write-safety case before any write registration;
- clean wheel install and console-script smoke.

### Stop and investigate rather than guess when

- corrected OpenAPI and live evidence disagree;
- a request or response schema cannot be represented without `Any`;
- a single-get, delete, status, or service route is uncertain;
- a money unit is not explicitly proven;
- a PUT omission rule is unknown;
- a write lacks a deterministic preview or read-back story;
- target MCP clients do not visibly present elicitation to a human;
- a retry could follow a dispatched mutation;
- a requested abstraction exists only for a hypothetical future endpoint.

Record unresolved behavior plainly. Do not silently invent it.

### Exact final gates

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q -m "not live"
uv build
```

Then install the exact built wheel into a clean environment and prove:

```bash
python -c "from clockify import ClockifyClient; print(ClockifyClient.__name__)"
clockify-mcp --help
```

For a release containing MCP writes, also run every ship condition in `MCP_WRITE_SAFETY_PLAN.md` and attach target-client compatibility evidence. No other gate may substitute for these.
