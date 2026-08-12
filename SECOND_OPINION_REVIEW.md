# Independent second-opinion review

## Executive conclusion

The Direction A architecture is coherent and unusually well covered. The complete 168-operation SDK surface reconciles mechanically, the shipped MCP is structurally read-only, the exact built wheel works on every locally available supported Python version, and all 14 targeted hand mutants turned tests red.

It is not ready for a read-only release. Two independently reproduced security-contract defects remain in the shared HTTP/error path: caller-controlled authority and credential headers survive into authenticated requests, and attacker-controlled upstream JSON can reflect configured secrets into SDK exceptions and MCP output. The distribution also advertises inline typing without shipping `py.typed`, and CI does not exercise the installed MCP artifact or the full declared Python range.

No production code was changed. This file is the only persistent review artifact.

## 1. Reviewed HEAD and repository state

- Repository: `/Users/15x/Downloads/WORKING/addons-me/2mcp`
- Branch: `main`
- HEAD: `80a92f09cdeda4c0224d90da091382e9fc394a26`
- Initial worktree: clean.
- Refs: only `refs/heads/main` at the reviewed HEAD.
- Remotes: none configured.
- Tags: none.
- Recent commits, newest first:
  - `80a92f0 fix(review): close round-3 review findings`
  - `232f06a fix review F-A/F-B...`
  - `87e1553 docs...`
  - `6c0d359 fixes...`
- Sibling evidence repository: `/Users/15x/Downloads/WORKING/addons-me/clockify-ts-sdk`, branch `main`, HEAD `d7091a44a1b95d4918fa17a7f9b174bf668a9136`, clean relative to `origin/main`. It was not modified.
- Available interpreters used for artifact testing: CPython 3.11.11, 3.13.13, and 3.14.5. Python 3.12 was not installed.
- Locked/runtime tool versions observed after sync: `httpx 0.28.1`, `pydantic 2.13.4`, `mcp 2.0.0`, `pyright 1.1.411`, `pytest 9.1.1`, `pytest-asyncio 1.4.0`, `PyYAML 6.0.3`, and `ruff 0.16.2`.
- The source tree has two shipped packages, `src/clockify` and `src/clockify_mcp`; tests are split into contract, importer, unit, MCP, and separately marked live suites. There is one workflow, `.github/workflows/ci.yml`.

The initial anti-anchored audit was completed before reading `ADVERSARIAL_REVIEW.md` or `IMPLEMENTATION_STATUS.md`. Preliminary notes were kept outside the repository and deleted after consolidation. One disposable worktree was used for the hand mutants and removed before this report was finalized.

## 2. Authoritative source reconciliation

The governing documents were read in full before the prior review/status documents. Their reviewed SHA-256 hashes are:

| Source | SHA-256 |
|---|---|
| `docs/port/MASTER_IMPLEMENTATION_PLAN.md` | `98cd9d525d6b90d7c0f8fd72df04d4c30a43d1034d00a25d7b050cbe983f9513` |
| `docs/port/OPERATION_PORT_MANIFEST.md` | `c980a24fcf87c91b504a500744e1c8a3cda9b5116a78135769695d45a30e2846` |
| `docs/port/MCP_WRITE_SAFETY_PLAN.md` | `f278b1ddbcd846b31e31d54ccd9942b460f13bf0e5fc5e16943d0b6ded200311` |

The manifest was parsed independently rather than trusted through repository count assertions. It contains 168 records, 168 unique operation IDs, 29 resources, and 168 unique public `(resource, method)` pairs. The parsed records exactly match the runtime registry for operation ID, HTTP method, path, service, mutation classification, and ordered Python/wire query names.

An AST pass found exactly 168 explicit public resource methods and confirmed that every method references its expected operation constant. The reverse mapping found no extra public operation method and no manifest operation lacking a public method. Runtime type-hint resolution succeeded for all 168 methods.

The independent counts are:

| Contract | Observed |
|---|---:|
| Operations | 168 |
| Explicit resources | 29 |
| Explicit public methods | 168 |
| Reads | 62: 49 GET, 13 POST |
| Writes | 106: 39 POST, 29 PUT, 23 DELETE, 15 PATCH |
| Regular / reports / audit routing | 157 / 10 / 1 |
| Multipart operations | 3 |
| Reachable component-schema roots from pinned corrected OpenAPI | 339 |
| Raw MCP reads / workflows / total | 60 / 5 / 65 |

The importer regenerated 339 roots into a temporary directory from the pinned sibling corrected OpenAPI. After applying the repository's Ruff formatting, all generated domain model modules matched the committed model output. The only textual difference was first-party import ordering in generated `__init__.py`, caused by formatting outside the repository package path; exports were semantically identical. All generated model modules imported and rebuilt. Request models reject unknown fields and response models preserve additive upstream fields, as required.

No governing conflict was silently reconciled. The current implementation wins over status prose where the status is stale, while the three port plans govern acceptance. Current official MCP behavior was needed only for the installed stdio-client proof; the installed official `mcp 2.0.0` client was used directly.

## 3. Baseline command results

All requested non-live gates ran at the reviewed HEAD:

| Command | Exit | Result |
|---|---:|---|
| `uv sync --all-extras --dev` | 0 | Resolved 45 packages; audited 42 packages. |
| `uv run ruff check .` | 0 | All checks passed. |
| `uv run ruff format --check .` | 0 | 246 files already formatted. |
| `uv run pyright` | 0 | 0 errors, 0 warnings, 0 notes. |
| `uv run pytest -q -m "not live"` | 0 | 425 passed, 6 deselected in 7.56 seconds. |
| `uv build` | 0 | Wheel and sdist built successfully. |

The live suite was intentionally not rerun: it requires a verified sacrificial workspace and performs mutations. Prior claims about a live run are status evidence, not current proof from this review.

Fresh artifact hashes were:

- wheel: `23ce6b69569b4ad014b7f21f86cdbe222f88adee002606a98aacaf68db245d51`
- sdist: `b709ad875ebd02d9cf9b21daf67858eabd5512ea1ebfa4556423149b58fdaef4`

Two independent builds produced byte-identical wheel and sdist hashes.

## 4. Installed-artifact proof

The fresh wheel contains 168 archive entries across `clockify`, `clockify_mcp`, and distribution metadata. It includes the dormant write-safety implementation but no `py.typed` marker. The sdist contains source, tests, `README.md`, `LICENSE`, `SECURITY.md`, `pyproject.toml`, and `.gitignore`; it intentionally omits generated build output, caches, local configuration, docs, examples, changelog, and `uv.lock` under the current explicit include rule.

The wheel metadata identifies `clockify-python-115` version `0.1.0`, MIT license, Python `>=3.11`, and the optional `mcp` extra. Clean wheel-only virtual environments were created for CPython 3.11, 3.13, and 3.14. In all three:

- `from clockify import ClockifyClient; print(ClockifyClient.__name__)` printed `ClockifyClient`;
- installed metadata reported version `0.1.0`;
- the MCP extra resolved to `mcp 2.0.0`;
- `clockify-mcp --help` exited 0, wrote no stdout bytes, and wrote 157 help bytes to stderr.

A separate CPython 3.14 environment installed the exact wheel without extras. `import clockify` succeeded and the `mcp` distribution was absent, proving the core SDK does not require MCP dependencies.

An official `mcp.client.session.ClientSession` over `mcp.client.stdio.stdio_client` spawned the installed `clockify-mcp` entry point on CPython 3.11 and 3.14. Both sessions initialized as server `clockify`; `tools/list` returned exactly the same 65 names: 60 raw reads and the five specified workflows, with zero write operation names. A controlled invocation of `clockify_shared_reports_view_public` using an unsupported PDF format returned an MCP tool error before network with the documented JSON/CSV-only message. Server startup, initialization, `tools/list`, and that rejected call emitted no application text on stdout and made no Clockify request. This proves installed protocol behavior and the pre-network boundary; it is not a successful live-host read.

## 5. Complete SDK reconciliation

The complete bidirectional reconciliation passed:

```text
168 manifest records
  -> 168 static operation constants
  -> 168 registry entries
  -> 168 explicit resource methods
  -> matching method/path/service/mutation/query ordering
  -> resolvable public annotations and models
  -> focused wiring fixtures/tests
```

The reverse AST pass found exactly one operation reference per explicit method and no orphaned method or record. There is one runtime operation truth: static operation modules plus the registry. Models are committed static Pydantic v2 classes; runtime generation is absent.

The risk-weighted sample was exhaustive for the requested categories: all 13 POST reads, all three multipart operations, all 11 non-regular-host operations, all three binary/content-negotiated operations, all five lifecycle-constrained operations, and all 19 operations classified with mixed or not-fully-proven replacement behavior. The review also traced every money-scale deviation, pagination variant, the invoice-payment create response/ID limitation, and dead or missing single-GET routes. Existing focused wiring tests were included in the 425-test baseline.

Confirmed behavior includes exact alias/wire-name encoding, omission versus explicit null, list/envelope/bytes/text/no-content/negotiated decoding, caller-owned file lifetime, and explicit replacement-risk documentation. Invoice-payment creation intentionally returns the invoice response supplied by Clockify rather than inventing an unproven payment-ID recovery call; the limitation is documented and is not a defect under the governing plan's “recover or explicitly fail/state the limitation” rule.

## 6. Transport and reliability findings

The shared transport correctly enforces credential XOR at configuration, safely encodes path components including dot segments, refuses redirects, validates configured custom hosts unless explicitly allowed, reuses one async client, preserves cancellation, closes retried responses, distinguishes POST reads from writes, retries only semantic reads, and maps ambiguous write transport failures to the uncertainty error. Pagination stop rules cover true/false `Last-Page`, short and empty pages, repetition, and the maximum-page cap.

Three transport defects were reproduced:

- **SO-01:** caller-controlled `Host` and opposite credential headers survive compilation and authenticated dispatch.
- **SO-02:** upstream JSON error content can reflect the configured credential into SDK and MCP errors and is unbounded.
- **SO-03:** valid HTTP-date `Retry-After` values are ignored.

Their complete finding records are in section 13.

## 7. Read-MCP findings

The read-MCP security claims held under source inspection, installed stdio execution, and focused mutants:

- Exactly 60 raw read tools and five named workflows register, for 65 total.
- Binary-only reads are excluded. Shared-report PDF/XLSX is rejected before transport.
- Default-server import tracing does not load any `clockify_mcp.writes` module.
- Construction and `tools/list` perform no HTTP request.
- Raw tools map only to the explicitly registered semantic reads.
- Workflows receive slot-restricted read capabilities, not the general client.
- `ReadOnlyExecutor._require_read` is the final runtime boundary for compile, execute, and compiled dispatch (`src/clockify/_transport/executor.py:218-240`).
- There is no arbitrary URL/method tool or fallback write path.
- Tool results are structured, and the installed stdio process keeps protocol output isolated from help/error text.

Mutating the boundary, tool mapping, imports, workflow capability, format rejection, or tool counts caused focused tests to fail. No read-MCP-specific defect was confirmed beyond the shared transport/error findings SO-01 and SO-02.

## 8. Dormant write-safety findings

The default server still registers zero writes. The dormant core and the sole `clockify_tags_create` adapter were reviewed separately and do not change that read-only fact.

The implemented safety design binds canonical arguments, tool, workspace, principal, request-state audience/expiry, exact stored steps, operation order, and request digests. It rejects tampering and replay, consumes atomically under 100-way concurrency, refuses automatic write retry, preserves cancellation/partial/ambiguous outcomes, runs reconciliation after preserving the mutation result, and limits builders to read capabilities. All eight requested write-safety mutants turned tests red.

Two dormant defects remain:

- **SO-06:** the byte limit counts Unicode code points and omits retained reconciliation fields.
- **SO-07:** `max_pending` does not bound live tombstones, so issuance/consumption rate can grow memory without a count bound during the TTL window.

These block future write registration, not the current zero-write MCP release by themselves. Real approval behavior is still unproven in two target MCP host UIs; no in-memory protocol result is presented as human-approval proof.

## 9. Packaging and CI findings

Package identity, version, description, MIT license, minimum Python, import packages, optional dependency, and console entry point are internally consistent. Artifacts were byte-reproducible in two local builds and clean installation worked on 3.11, 3.13, and 3.14.

Three release-surface gaps remain:

- **SO-04:** `Typing :: Typed` is advertised but the wheel has no PEP 561 marker.
- **SO-05:** CI installs the wheel without `[mcp]` and only imports packages; it never executes the installed console or official-client stdio flow, and omits declared Python 3.12. It also lacks coverage for newest-supported Python under the open-ended `>=3.11` requirement.
- **SO-08:** user-facing documentation does not say the project is independent/unofficial, and its destructive quickstart uses a fixed tag name despite the documented reservation behavior after deletion.

CI does independently clone the sibling repository at the exact pinned SHA, so corrected-OpenAPI reconciliation does not depend on a developer's local sibling checkout. There is no release workflow, remote, tag, or published PyPI project at the reviewed point; `https://pypi.org/pypi/clockify-python-115/json` returned 404. Therefore the README's `uv add` commands are syntactically correct future installation commands but cannot presently install from PyPI. That is an external publication state, not evidence that the local artifact is broken.

## 10. Maintainability assessment

The implementation is understandable and follows the intended dependency direction. There is no runtime public-method generation, `__getattr__`, decorator scanning, generic CRUD framework, or import-time operation discovery. Operation constants, request compilation, response decoding, resource methods, and MCP registration have distinct responsibilities. Resource modules are repetitive by design but make endpoint ownership easy to locate.

A normal endpoint addition requires updating the authoritative manifest/spec evidence, regenerating or selecting models when schemas change, adding one static operation record to the appropriate domain module, exporting it through the registry, adding one explicit resource method, adding a focused wiring fixture/test, and—only for a semantic read—making an explicit MCP registration decision. This is several files but few concepts, and the complete reconciliation prevents silent one-sided additions.

A contributor can answer the requested navigation questions directly:

- endpoint definition: `src/clockify/operations/<domain>.py` and `operations.registry`;
- public method: `src/clockify/resources/<domain>.py`;
- model: `src/clockify/models/<domain>.py`;
- request compilation: `src/clockify/_transport/encode.py` and `executor.py`;
- read-only enforcement: `ReadOnlyExecutor`;
- executable proof: `tests/contract/wiring`, transport tests, and MCP tests;
- extension process: static record, explicit method, registry/export, focused proof.

The real maintainability hotspot is duplicated/partial policy logic at security boundaries: two numeric-only `Retry-After` parsers exist, and error safety is split between SDK decoding and MCP conversion. **SO-10** also records stale operator ceremony: `CLAUDE.md` still directs every fresh session to a completed status file's “Next exact action,” while a large implementation prompt remains in the repository after implementation.

## 11. Secret-hygiene result

No credential value is printed in this report.

- Current tracked-file and high-confidence pattern scans found no credential.
- Current non-ignored untracked files were absent. Local `.env`, `.mcp.json`, `.remember`, virtual environments, caches, and build outputs are ignored.
- Current reachable history, refs, tags, fresh wheel, and fresh sdist had no match for the actual locally configured credential values.
- Artifact filename and content scans found no suspicious secret-bearing file.
- Reflog/unreachable-object scanning is a separate result: one actual local credential value matched unreachable blob `88ab0df5bfd36815c7073531cbd54f3b73f826d6`, associated with `.mcp.json` in reflog-only commit `63dd88ce7b0c814fd5fed93f22d2e308fc1f3eb7`. It is not reachable from a current ref and is not present in a build artifact, but remains locally recoverable until reflog expiry and garbage collection. See SO-09.
- Error-path testing disproved runtime redaction: a mock upstream response that reflected the configured credential placed it in exception text/body and then in MCP tool error text. See SO-02.

## 12. Targeted mutant results

One disposable worktree was created at the reviewed HEAD. Each mutation was applied alone, its narrow test was run, and the worktree was restored before the next mutation. All 14 mutants were detected:

| Mutant | Detection result |
|---|---|
| Disable `ReadOnlyExecutor` mutation rejection | Read-only boundary test failed; mutation reached the next layer. |
| Map a raw read tool to tag creation | End-to-end raw-tool test failed. |
| Import the write adapter in the default server | no-write-module import invariant failed and identified the write modules. |
| Give a workflow the general client | restricted-capability test failed. |
| Allow PDF/XLSX through shared-report MCP | pre-network format-rejection test failed. |
| Omit raw tag registration | exact 60/5/65 contract failed. |
| Leave a consumed nonce pending/no tombstone | single-use and 100-way concurrency tests failed; the mutant allowed 100 permits. |
| Remove principal binding | mismatch test failed. |
| Remove workspace binding | workspace-tamper test failed. |
| Remove argument binding | mismatch test failed. |
| Dispatch the caller-supplied step, not stored permit step | stored-identity test failed. |
| Enable write retry | two mutation-outcome tests failed and observed three calls. |
| Bypass prune/expiry | exact TTL test failed. |
| Bypass plan-byte/capacity checks | three focused limit tests failed. |

The disposable worktree was clean before removal, then removed and pruned. Only the main worktree remains.

## 13. Confirmed findings

### SO-01 — caller-controlled authority and credential headers reach authenticated requests

- **Severity:** MEDIUM
- **Affected files:** `src/clockify/_transport/executor.py:54-79`, `src/clockify/_transport/executor.py:97-114`; missing regression coverage in `tests/unit/transport/test_executor.py`.
- **Violated invariant:** exactly one credential is sent, and final destination/authority is validated before authentication. Preserving ordinary caller headers does not authorize a caller to override HTTP authority or inject the opposite supported credential.
- **Exact reproduction:** execute a raw read through an `HttpExecutor` configured with an API key and an `httpx.MockTransport`, passing `headers={"X-Addon-Token": "caller-not-real"}`. The captured request contains both one `X-Api-Key` and one `X-Addon-Token`. Repeat with `headers={"Host": "attacker.invalid"}`: the URL remains `https://api.clockify.me/...`, but the captured HTTP `Host` header is `attacker.invalid` and the configured credential is attached. Source explains the result: arbitrary caller headers win at lines 69-70, destination validation examines only `compiled.url`, and credential attachment follows without a protected-header check at lines 104-113.
- **Real consequence:** a public raw caller can send two supported credentials or route an authenticated request under a caller-chosen HTTP authority value. Depending on proxy/origin behavior, this can misroute credentials or make authentication identity ambiguous. URL-host validation alone does not validate the effective `Host` header.
- **Smallest correct repair:** reject protected headers case-insensitively at compilation/dispatch (`Host`/authority forms, `X-Api-Key`, and `X-Addon-Token`), then attach exactly the configured credential after URL and authority validation. Continue preserving non-security-sensitive caller headers and caller `X-Request-Id` as documented.
- **Required regression test:** parameterize case variants of both credential names and `Host`; prove rejection happens before `MockTransport`, prove ordinary headers and caller request IDs survive, and prove an accepted request has exactly one configured credential and URL-consistent authority.
- **False-positive checks:** constructor credential XOR already works; redirects are disabled; custom service URLs require opt-in; URL validation does run before credential attachment; HTTPX's case-insensitive header container does not remove a distinct opposite credential and demonstrably transmits the overridden `Host`.
- **Blocks:** read-only release.

### SO-02 — untrusted upstream JSON can leak a configured secret and grow error output without a bound

- **Severity:** MEDIUM
- **Affected files:** `src/clockify/_transport/decode.py:110-134`, `src/clockify_mcp/errors.py:17-30`; error classes retain the parsed body.
- **Violated invariant:** secrets never appear in logs, exceptions, `repr`, or MCP output; upstream error context is preserved only when safe and bounded.
- **Exact reproduction:** configure a mock SDK client with a test credential and return an error JSON object whose `message` and another field equal that same configured value. Catch `ClockifyAPIError`: both `str(exc)` and `repr(exc.body)` contain the value. Pass it to `to_tool_error`: line 25 interpolates the SDK exception and the MCP error contains it too. A separate JSON `message` containing a very large string is retained/interpolated without the 500-character bound applied only to non-JSON text at line 121.
- **Real consequence:** a compromised/misconfigured upstream, reflected request data, proxy, or test service can echo a credential into application exception telemetry or directly into MCP model-visible output. Large JSON errors also allow attacker-controlled memory/output amplification.
- **Smallest correct repair:** centralize bounded error sanitization in the SDK. Redact the configured credential and authorization-like values before constructing messages or retained public bodies, bound parsed messages/bodies, and have MCP render only stable sanitized fields rather than the full SDK exception. Do not log or retain raw response headers/bodies when they fail the safety policy.
- **Required regression test:** use exact configured API-key and add-on-token values reflected at multiple JSON depths and in text responses; assert absence from `str`, `repr`, stored public fields, and MCP error text. Include a megabyte JSON message and assert deterministic bounds while request ID, operation ID, status, safe API code, and safe retry timing remain useful.
- **False-positive checks:** repository fixtures do not contain production credentials; non-JSON text is already sliced; rate-limit MCP output avoids the body. These facts do not protect general JSON API errors, and the reproduction uses only `MockTransport`.
- **Blocks:** read-only release.

### SO-03 — valid HTTP-date `Retry-After` is ignored

- **Severity:** LOW
- **Affected files:** duplicated parsers in `src/clockify/_transport/decode.py:89-97` and `src/clockify/_transport/executor.py:243-251`.
- **Violated invariant:** valid `Retry-After` is honored correctly for rate-limit context and retry scheduling. RFC 9110 permits either an HTTP-date or delay-seconds.
- **Exact reproduction:** pass an `httpx.Response(429, headers={"Retry-After": "Wed, 12 Aug 2026 08:30:00 GMT"})` to either parser. Both return `None`; they only call `float(raw)`. See [RFC 9110 Retry-After](https://www.rfc-editor.org/rfc/rfc9110.html).
- **Real consequence:** semantic reads retry on backoff rather than the server-directed time, and rate-limit errors omit valid timing context. This can cause premature traffic or unnecessarily late recovery.
- **Smallest correct repair:** replace both copies with one parser supporting non-negative delay-seconds and RFC HTTP-date relative to a supplied/testable clock, treating past dates as zero and malformed values as absent. Continue applying the retry policy's maximum sleep clamp.
- **Required regression test:** future HTTP-date, past date, integer/fractional delay, negative delay, malformed date, missing header, and a deterministic Date/clock case through the actual retry loop.
- **False-positive checks:** numeric non-negative values work; negative/malformed values fail closed; RFC syntax explicitly includes HTTP-date, so this is not a vendor-extension request.
- **Blocks:** neither.

### SO-04 — the typed distribution lacks the required PEP 561 marker

- **Severity:** MEDIUM
- **Affected files:** `pyproject.toml:17-25`, wheel packaging at `pyproject.toml:42-43`, and absent `src/clockify/py.typed` (also absent for any intended public `clockify_mcp` typing contract).
- **Violated invariant:** published classifiers and artifact contents truthfully expose the SDK's public typing contract.
- **Exact reproduction:** inspect the exact fresh wheel: no `clockify/py.typed` exists although metadata contains `Classifier: Typing :: Typed`. Install that wheel in a clean environment with mypy 2.3.0 and type-check `from clockify import ClockifyClient`; mypy reports that `clockify` is installed but missing stubs or a `py.typed` marker and reveals `ClockifyClient` as `Any`. [PEP 561](https://peps.python.org/pep-0561/) requires an inline-typed package to include the marker.
- **Real consequence:** downstream standard type checkers ignore the SDK's annotations, so the primary value of a typed SDK disappears after installation while repository-local pyright remains green.
- **Smallest correct repair:** add `src/clockify/py.typed`, ensure Hatch includes it, and decide/document whether `clockify_mcp` is also a supported typed public package. Keep the classifier only when installed-package proof passes.
- **Required regression test:** inspect the built wheel for the marker and run a clean-environment downstream mypy or pyright consumer against the installed wheel, asserting a deliberately wrong SDK call is rejected and exported types are not `Any`.
- **False-positive checks:** source-tree pyright is strict and green, but PEP 561 discovery is an installed-distribution concern. The wheel was inspected directly and the clean consumer did not use source paths.
- **Blocks:** read-only release.

### SO-05 — CI does not prove the installed MCP artifact or full declared Python support

- **Severity:** MEDIUM
- **Affected files:** `.github/workflows/ci.yml:9-39`, `pyproject.toml:11`, `pyproject.toml:21-24`.
- **Violated invariant:** clean-checkout CI carries the required installed-artifact evidence for supported interpreters, imports, console command, stdio initialization/tool contract, and optional dependency separation.
- **Exact reproduction:** inspect the only workflow. Its matrix is 3.11 and 3.13. Lines 35-39 install `dist/*.whl` without `[mcp]` and only run `import clockify, clockify_mcp`; they do not invoke `clockify-mcp`, initialize with an official MCP client, list tools, or verify SDK-only import without MCP. Python 3.12 is explicitly classified but absent. The open-ended `>=3.11` metadata has no strategy for newest Python.
- **Real consequence:** CI can stay green if the wheel entry point, extra metadata, stdio protocol, tool registration, stdout isolation, or Python 3.12 compatibility regresses. The stronger proof exists only as this review's local receipt.
- **Smallest correct repair:** add artifact-consumer jobs that install the exact wheel as core-only and `[mcp]`; run the import, console, and official stdio initialize/list/controlled-call checks; include 3.12 and define a deliberate newest-Python policy (currently 3.14 locally) or cap `requires-python` to what CI supports.
- **Required regression test:** the CI consumer steps themselves, with assertions for 65 exact names, zero writes, no startup/list network, stdout protocol-only, and core import in an environment where MCP is absent.
- **False-positive checks:** source tests already exercise stdio and CI does build a wheel; local clean installs passed 3.11/3.13/3.14. The finding is the missing durable release gate, not a claim that the current wheel fails.
- **Blocks:** read-only release.

### SO-06 — dormant plan byte limit is bypassable through Unicode and reconciliation

- **Severity:** MEDIUM
- **Affected files:** `src/clockify_mcp/writes/nonce_store.py:92-118`, retained fields in `src/clockify_mcp/writes/plan.py:67-88`.
- **Violated invariant:** the configured byte cap accounts for every string/byte retained by a pending write plan.
- **Exact reproduction:** create `InMemoryNonceStore(max_plan_bytes=100)` and issue a plan whose warning is `"😀" * 30`; `_plan_size` uses `len(str)`, counts 30, and accepts 120 UTF-8 bytes. Separately issue a minimal plan with `ReconciliationPlan(description="x" * 10_000)` under the same cap; it is accepted because reconciliation is omitted from `_plan_size`, although it remains reachable from the stored `WritePlan`.
- **Real consequence:** once writes register, a caller can retain materially more process memory per pending confirmation than the configured security limit promises.
- **Smallest correct repair:** compute the size of one canonical serialization of the entire retained plan and measure its byte length, or explicitly count every retained value after UTF-8 encoding, including reconciliation and future fields.
- **Required regression test:** multibyte strings across every textual field, oversized reconciliation fields, boundary-equal/one-byte-over cases, and a structural test that adding a retained dataclass field cannot silently escape accounting.
- **False-positive checks:** `body_json` is already bytes and correctly byte-counted; ordinary ASCII fields make character and byte counts equal; current MCP imports/registers no writes. The reproduced objects are nevertheless retained by the dormant store.
- **Blocks:** future write registration.

### SO-07 — dormant tombstones have no count/capacity bound

- **Severity:** LOW
- **Affected files:** `src/clockify_mcp/writes/nonce_store.py:65-90` and consume/tombstone insertion paths in the same module.
- **Violated invariant:** nonce-store limits prevent unbounded in-process accumulation under adversarial request rate while retaining replay protection.
- **Exact reproduction:** instantiate `InMemoryNonceStore(max_pending=1, ttl=300)` and sequentially issue and consume 2,000 unique records without advancing the clock. Pending count returns to zero after each consume, but `_tombstones` reaches 2,000; `max_pending` does not constrain it.
- **Real consequence:** after write registration, a principal that stays within one concurrent pending item can grow memory linearly with completed confirmations during the TTL window. TTL bounds duration, not request rate.
- **Smallest correct repair:** impose a documented combined-entry/tombstone capacity and fail issuance before replay protection would need unsafe eviction, or add a rate/cap policy whose eviction semantics cannot make a consumed nonce reusable.
- **Required regression test:** high-rate sequential consume beyond the configured bound, exact expiry pruning, replay preservation at capacity, and concurrency around the limit.
- **False-positive checks:** expired tombstones are pruned and current writes are unregistered. This is not lifetime-unbounded storage, but it is count-unbounded for any fixed TTL under unbounded rate.
- **Blocks:** future write registration.

### SO-08 — release documentation omits independence and gives a non-repeatable destructive quickstart

- **Severity:** LOW
- **Affected files:** `README.md:1-53`, especially lines 27-28; related reservation evidence in resource/behavior documentation.
- **Violated invariant:** user-facing docs clearly distinguish SDK writes, disabled MCP writes, and independent/unofficial status, and examples are safe and repeatable against the installed artifact.
- **Exact reproduction:** search the README for `independent` or `unofficial`: neither appears. Run the documented quickstart twice against one workspace: it creates then deletes a tag named exactly `example`; the repository's own behavior evidence says deleted tag/project/client names can remain reserved, so the second create can fail. The snippet also performs a real mutation without labeling the workspace/destructive consequence.
- **Real consequence:** users can mistake the distribution for an official Clockify package and can copy a first-run example that leaves a reserved name and fails on reuse. The docs do correctly state SDK writes exist and MCP is read-only, but not all three required distinctions.
- **Smallest correct repair:** add a concise independent/unofficial statement; make the first quickstart read-only; move writes to a clearly labeled sacrificial-workspace example with a unique generated name and the reservation caveat. Add installed-artifact examples for errors and multipart/lifecycle behavior as required by the plan.
- **Required regression test:** execute the read-only quickstart with a mock transport against the installed wheel and add a documentation assertion/lint for the three release distinctions. Any write example should use a deterministic mock plus unique-name construction.
- **False-positive checks:** the `-115` distribution suffix creates distance and README already says MCP is read-only; neither substitutes for an explicit user-facing independence statement or makes the fixed destructive example repeatable.
- **Blocks:** read-only release.

### SO-09 — an actual local credential remains in reflog-only unreachable Git data

- **Severity:** LOW
- **Affected files:** local Git object/reflog storage only; unreachable blob `88ab0df5bfd36815c7073531cbd54f3b73f826d6` from reflog-only commit `63dd88ce7b0c814fd5fed93f22d2e308fc1f3eb7` (historical path `.mcp.json`).
- **Violated invariant:** secret-hygiene reporting must distinguish clean reachable release history from locally recoverable historical credentials.
- **Exact reproduction:** read current ignored credential values internally without printing them, hash/search Git blobs, and classify matching objects by reachability and reflog. Two local values were checked: zero matches in tracked files, reachable refs, or artifacts; one value matched the named unreachable blob and its reflog-only commit.
- **Real consequence:** the value is not included by a normal push of current refs, but remains recoverable by any process/user with access to this local repository. If it was ever a real credential, deletion from the worktree did not revoke it.
- **Smallest correct repair:** rotate/revoke the affected credential first, then—outside this review—expire the relevant reflog and garbage-collect unreachable objects after preserving any legitimately needed recovery history.
- **Required regression test:** repeat the value-aware scan without printing the value and require zero matches separately for current files, reachable objects, reflogs/unreachable objects, and built artifacts.
- **False-positive checks:** the match used the actual local value, not only a key-name regex; the object is unreachable from current refs and absent from wheel/sdist. This is local hygiene, not a claim that the release artifact contains a secret.
- **Blocks:** neither.

### SO-10 — completed implementation still routes agents through stale continuation ceremony

- **Severity:** LOW
- **Affected files:** `CLAUDE.md:3-5`, `CLAUDE.md:36-46`, `CLAUDE_CODE_CLOCKIFY_PYTHON_IMPLEMENTATION_PROMPT.md`, and the completion-oriented status workflow.
- **Violated invariant:** repository instructions describe the current maintenance workflow rather than a completed implementation campaign's temporary continuation mechanism.
- **Exact reproduction:** read `CLAUDE.md`: every fresh session is told to read `IMPLEMENTATION_STATUS.md`, find “Next exact action,” and “continue” the current phase. At the reviewed completed HEAD, the large original implementation prompt is also still a root-level operational document. Git/history and the current 168-operation implementation show the greenfield campaign is no longer the normal task state.
- **Real consequence:** a human or coding agent can treat stale status prose as authority, resume obsolete work, or spend time maintaining checks/documents tied to the implementation campaign rather than product behavior.
- **Smallest correct repair:** replace the continuation ritual with a short maintenance/onboarding guide anchored to current source and gates; archive or remove the one-shot implementation prompt and keep historical status explicitly non-authoritative.
- **Required regression test:** no code test is appropriate. A lightweight documentation check should ensure the active guide does not require a “Next exact action” in a historical status file and still preserves the authoritative plan/pinned-spec boundaries.
- **False-positive checks:** the guide contains valuable architecture, path, and safety constraints that should remain. The finding concerns the completed-campaign continuation instructions, not the existence of repository guidance.
- **Blocks:** neither.

## 14. Rejected hypotheses and why

- **The registry counts might merely agree with themselves.** Rejected by independent manifest parsing, AST method tracing, runtime type-hint resolution, and temporary regeneration from the pinned OpenAPI.
- **A hidden MCP write might register despite tool counts.** Rejected by exact installed tool-name inspection, default-server import tracing, operation mutation classification, and an import mutant that turned the invariant test red.
- **A workflow could reach a general/raw mutable client.** Rejected by slot-surface inspection, end-to-end capability tests, final `ReadOnlyExecutor` enforcement, and the general-client mutant.
- **A tool annotation rather than execution code might be the read boundary.** Rejected: changing the executor alone caused a mutation to proceed to the next layer and fail the focused tripwire.
- **PDF/XLSX might reach the reports host.** Rejected by the installed official-client call and format-allow mutant; the normal path fails before transport.
- **Writes might automatically retry because they use POST.** Rejected: retry eligibility uses semantic mutation metadata, POST reads retry, mutations do not, and the write-retry mutant observed three calls and failed tests.
- **Path values `.`/`..` or slashes might alter the route.** Rejected by encoded-path tests and compiled-request inspection: dangerous path arguments are percent-encoded as components.
- **Response-kind dispatch might coerce unknown binary to text.** Rejected: content negotiation preserves unknown binary as bytes and tests cover JSON/text/binary/no-content branches.
- **Pagination could loop forever on repeated content.** Rejected by repeated-page detection and a maximum-page cap in addition to header/short/empty termination.
- **Model generation might happen at runtime.** Rejected by import/source tracing; models and operation records are committed static code.
- **The wheel might accidentally depend on a source checkout.** Rejected by clean wheel-only environments and SDK-only import without MCP installed.
- **Current release history/artifacts contain a credential.** Rejected for reachable refs and fresh artifacts by actual-value scanning. The separate reflog-only issue is SO-09 and is not promoted to a release-artifact leak.
- **The `validate_destination` path-prefix comparison alone is an exploitable arbitrary-URL escape.** No public path was found that lets a caller replace the compiled scheme/host or inject an absolute URL; path arguments are quoted. The effective `Host` header bypass is instead the concrete SO-01.
- **The documented invoice-payment create behavior necessarily loses a recoverable payment ID.** Rejected as a defect: current primary evidence does not establish a safe universal recovery route, and the limitation is explicit rather than silently fabricated.

## 15. Comparison with the prior review

This comparison was performed only after the independent conclusions above were recorded.

The prior review found real defects that are now fixed at the reviewed HEAD, including stored-step dispatch identity, evidence-gate enforcement, multipart byte handling, and tombstone lifetime documentation/behavior. Its conclusion that the static operation surface and read-only MCP architecture are fundamentally sound is supported by this audit and by stronger complete reconciliation plus installed-artifact proof.

It missed SO-01 (authority/opposite-credential injection), SO-02 (reflected secret/unbounded JSON errors), SO-03 (HTTP-date retry timing), SO-04 (missing PEP 561 marker), SO-05 (installed-MCP CI gap), the remaining byte-accounting bypasses in SO-06, the tombstone capacity issue in SO-07, and the release-documentation issue in SO-08.

It overstated secret hygiene by treating the sweep as complete despite an actual credential value remaining in reflog-only unreachable data. That is not a reachable release leak, but “zero actual-secret matches” was too broad without the explicit reachability split used here.

It also overstated current release proof where status prose substitutes for durable automation: a local/previous live receipt is not a current real-host result, and no release workflow exists. Status references to live-suite totals are internally stale/conflicting and were not used as current evidence. Conversely, this review does not repeat already-fixed findings as current defects.

The prior review's “READ-ONLY RELEASE READY” conclusion is therefore superseded by the reproduced read-release blockers in SO-01, SO-02, SO-04, SO-05, and SO-08.

## 16. Exact remaining external blockers

After source repairs and regression tests, the following evidence still requires external state or operator action:

1. Run the marked live SDK suite against a verified sacrificial Clockify workspace, with a unique run prefix and proven zero residue. This review did not make a real Clockify request.
2. Before any MCP write registration, obtain real approval/decline/cancel/replay receipts from each of the two intended MCP host UIs. Official in-memory Python client tests do not prove a human-visible approval boundary.
3. Resolve the dormant SO-06 and SO-07 findings and complete every remaining write-safety-plan ship condition before registering any write module.
4. Rotate the credential identified only by the internal value-aware scan, then deliberately expire/gc the local reflog-only object if recovery history is no longer needed. Do not regard garbage collection as revocation.
5. Establish an intentional publication path and release workflow, then publish and verify the immutable artifact before advertising the PyPI installation command as currently usable. At review time there is no remote, tag, release workflow, or PyPI project.

## 17. Final verdict

**FAIL — READ-ONLY RELEASE BLOCKER REMAINS**

Direction A remains the right foundation. The fail is not an architectural rejection: it is the consequence of reproducible release-boundary defects in authenticated header handling, error redaction, installed typing, CI artifact proof, and user-facing release documentation. The dormant write subsystem remains correctly unregistered and has its own separate blockers.

## 18. Direction A remediation closure — 2026-08-12

The verdict above describes the reviewed baseline. It is preserved as review
input. The following source-backed closure supersedes its release conclusion at
release-candidate code commit `e755016`.

| Finding | Current disposition | Durable proof |
|---|---|---|
| SO-01 | Fixed. Caller `Host`, `:authority`, `X-Api-Key`, and `X-Addon-Token` variants fail before dispatch; `Authorization` and ordinary caller headers remain supported. | Transport header matrix and final dispatch guard. |
| SO-02 | Fixed. Configured credential values, auth-like fields, nested data, headers, strings, depth, collection size, and body size are sanitized or bounded. MCP errors expose only stable safe fields. | Reflected-secret and oversized-error tests. |
| SO-03 | Fixed. One shared parser handles delay-seconds and RFC HTTP-date values, using `Date` or a UTC clock and clamping past dates to zero. | Retry-delay parameter matrix. |
| SO-04 | Fixed. Both import packages ship `py.typed`; the installed wheel passes a negative Pyright type check. | Exact-wheel verifier on Python 3.11–3.14. |
| SO-05 | Fixed. CI builds once, downloads the exact artifact, and runs clean core/MCP/stdio/type proof on Python 3.11–3.14. Release publication is isolated in a Trusted Publishing job. | Pinned workflows and CI contract test. |
| SO-06 | Fixed. The store measures canonical UTF-8 bytes for every retained dataclass field, including reconciliation and future fields. | Unicode, boundary, oversized-warning, and structural coverage tests. |
| SO-07 | Fixed. One combined capacity covers pending records and live tombstones; pruning occurs before admission. | Sequential and concurrent capacity tests. |
| SO-08 | Fixed. README states independence, leads with a read-only quickstart, separates SDK writes from MCP, and uses a unique sacrificial write example. | Documentation contract tests and typed examples. |
| SO-09 | Owner action remains. Reachable refs, tracked files, and artifacts contain no configured credential match. One local reflog-only unreachable blob still matches. | Value-aware scan; blob `88ab0df5bfd36815c7073531cbd54f3b73f826d6`. |
| SO-10 | Fixed. `CLAUDE.md` is now a maintenance guide and the completed campaign prompt is removed. | Documentation contract test. |

The 15-mutant campaign killed every required weakened boundary. The final
offline suite passed 459 tests with six live tests deselected. The authorized
live sacrificial suite then passed all six tests and left zero residue. Two
builds were byte-identical, and the exact wheel passed installed proof on
Python 3.11, 3.12, 3.13, and 3.14.

SO-09 does not place the credential in a release artifact or reachable ref, so
it does not block the local release candidate. The owner must rotate or revoke
the credential before relying on history cleanup. Remove the stale shell value,
then optionally expire the relevant reflog and garbage-collect unreachable
objects. Garbage collection is not credential revocation.

**DIRECTION A RELEASE READY — MCP WRITES REMAIN DISABLED**
