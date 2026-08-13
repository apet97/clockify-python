# Repository maintenance guide

## Purpose

- Maintain the released `clockify-python-115` package.
- Optimize for users, adopters, contributors, and maintainers.
- Use small direct changes that match the current architecture.
- Prefer evidence from source, tests, artifacts, and live boundaries.
- Do not restart the completed `0.1.0` perfection campaign.
- Do not add ceremony, speculative helpers, or dead code.

## Product contract

- The distribution name is `clockify-python-115`.
- The import package for the SDK is `clockify`.
- The import package for MCP is `clockify_mcp`.
- Python 3.11, 3.12, 3.13, and 3.14 are supported.
- The SDK has 168 operations on 29 resources.
- The SDK has 168 explicit public async methods.
- The default MCP server has 60 raw read tools.
- The default MCP server has five read workflows.
- The default MCP server has 65 tools in total.
- The default MCP server registers zero writes.
- The project is independent and unofficial.
- Do not imply endorsement by CAKE.com or Clockify.

## Sources of truth

- Use current source and tests as executable evidence.
- Use `src/clockify/operations/registry.py` for runtime operation truth.
- Use `docs/port/OPERATION_PORT_MANIFEST.md` for endpoint mappings.
- Use `docs/port/MCP_WRITE_SAFETY_PLAN.md` for MCP write conditions.
- Use `docs/api-deviations.md` for known API behavior differences.
- Use `docs/api-coverage.md` for the supported API surface.
- Use `docs/architecture.md` for dependency direction.
- Use `SECURITY.md` for security guarantees and reporting.
- Use `CHANGELOG.md` for user-visible version history.
- Treat old audits and implementation receipts as non-product history.
- Do not restore removed campaign documents to the repository.
- Verify documentation claims against the current checkout.

## Repository boundary

- Work in this repository unless the task names another path.
- Keep `../clockify-ts-sdk` read-only.
- Its pinned evidence commit is `d7091a44a1b95d4918fa17a7f9b174bf668a9136`.
- Do not edit, commit, reset, clean, or push the sibling repository.
- Preserve unrelated user changes in every worktree.
- Inspect `git status --short` before editing.
- Stop if an intended file contains unexplained user changes.
- Never expose credentials in commands, logs, diffs, or responses.

## Architecture map

- Client entry point: `src/clockify/client.py`.
- Configuration: `src/clockify/config.py`.
- Operation records: `src/clockify/operations/`.
- Operation registry: `src/clockify/operations/registry.py`.
- Pydantic models: `src/clockify/models/`.
- Public resources: `src/clockify/resources/`.
- Request encoding: `src/clockify/_transport/encode.py`.
- Response decoding: `src/clockify/_transport/decode.py`.
- Host validation: `src/clockify/_transport/hosts.py`.
- HTTP execution: `src/clockify/_transport/executor.py`.
- Read boundary: `src/clockify/_transport/read_only.py`.
- MCP server: `src/clockify_mcp/server.py`.
- MCP raw tools: `src/clockify_mcp/tools/`.
- MCP workflows: `src/clockify_mcp/workflows/`.
- Dormant write core: `src/clockify_mcp/writes/`.
- Keep dependency direction one-way toward MCP.
- The SDK must never import `clockify_mcp`.

## Operation design

- Keep one frozen `Operation` record per endpoint.
- Keep operation IDs unique.
- Keep public resource and method pairs unique.
- Keep one explicit resource method per operation.
- Do not generate public methods at runtime.
- Do not add generic CRUD machinery.
- Classify mutation by behavior, not only by HTTP verb.
- Preserve semantic POST reads as reads.
- Record service routing in the operation.
- Record request and response behavior explicitly.
- Preserve operation-specific pagination names.
- Preserve full-replacement risk for `PUT` operations.
- Add focused wiring evidence for each changed operation.

## Model design

- Use Pydantic v2 models.
- Request models must reject unknown fields.
- Response models must preserve additive upstream fields.
- Keep generated model output deterministic.
- Update the canonical importer before generated output.
- Run `scripts/import_openapi.py` for model regeneration tasks.
- Format generated output with the repository Ruff settings.
- Do not hand-edit broad generated surfaces.
- Keep `clockify/py.typed` in the wheel.
- Keep `clockify_mcp/py.typed` in the wheel.

## Transport rules

- Use one `httpx.AsyncClient` per `ClockifyClient`.
- Compile request data before network access.
- Validate the final destination before attaching credentials.
- Do not follow redirects.
- Preserve supported caller headers.
- Preserve `X-Request-Id` when supplied.
- Reject caller-supplied `Host`.
- Reject caller-supplied `:authority`.
- Reject caller-supplied `X-Api-Key`.
- Reject caller-supplied `X-Addon-Token`.
- Match protected header names case-insensitively.
- Never expose an arbitrary request URL.
- Never expose an arbitrary HTTP method.
- Never expose arbitrary authority or credential headers.
- Bound and sanitize public error details.
- Redact configured secrets from nested error data.
- Keep request IDs and safe API codes when available.
- Parse delay-seconds and HTTP-date `Retry-After` values.

## Retry and mutation safety

- Retry only operations classified as non-mutating.
- Never retry a write automatically.
- A configured retry policy does not override mutation semantics.
- Treat ambiguous write transport failure as an unknown outcome.
- Raise `MutationOutcomeUnknownError` for an ambiguous write result.
- Read current state before any manual retry.
- Keep retry delay bounded.
- Honor supported server retry timing.
- Test read and write behavior separately.
- Do not weaken safety to make a test pass.

## Default MCP server

- Build the default server with `build_read_only_server`.
- Building the server must not call Clockify.
- Use stdio as the default transport.
- Keep stdout protocol-only.
- Send diagnostics to stderr.
- Register read tools explicitly by domain.
- Register exactly five workflows.
- Route every raw tool through `ReadOnlyExecutor`.
- Give workflows only the restricted read capability.
- Do not import `clockify_mcp.writes` from the read server.
- Do not use annotations as enforcement.
- Reject PDF and XLSX shared-report formats before network access.
- Keep binary-only reads out of the MCP surface.
- Preserve tool names unless a versioned compatibility change is approved.

## MCP workflows

- Keep `clockify_status` read-only.
- Keep `clockify_workspace_overview` read-only.
- Keep `clockify_review_day` read-only.
- Keep `clockify_review_week` read-only.
- Keep `clockify_doctor` read-only.
- Use only the workflow read capability.
- Do not pass the full SDK client to workflow business logic.
- Require workspace context only when the workflow needs it.
- Convert SDK errors to bounded MCP tool errors.
- Test each workflow through the read boundary.

## Dormant MCP writes

- Dormant write code is not a public capability.
- Do not register a write in the default server.
- Do not claim a write is certified from offline tests alone.
- Follow `docs/port/MCP_WRITE_SAFETY_PLAN.md` for any write proposal.
- Require exact plan binding.
- Require deterministic human-readable previews.
- Require single-use atomic nonce consumption.
- Require bounded records and tombstones.
- Require final controlled execution.
- Require reconciliation for ambiguous outcomes.
- Require independent review.
- Require approval-UI evidence in two intended hosts.
- Keep write experiments limited to verified sacrificial workspaces.

## Documentation policy

- Keep repository Markdown product-facing or actively operational.
- Keep installation text aligned with public PyPI status.
- Lead with the read-only SDK and MCP experience.
- Separate direct SDK writes from MCP behavior.
- Mark mutating examples as sacrificial-workspace examples.
- Remove completed checklists and campaign receipts.
- Remove publication-pending language after publication.
- Do not duplicate the changelog in another tracked receipt.
- Use short sentences and active voice.
- Use one term for one concept.
- Preserve exact commands, identifiers, and error text.
- Check local Markdown links after deleting a document.

## Required local gates

- Run `uv run ruff check .`.
- Run `uv run ruff format --check .`.
- Run `uv run pyright`.
- Run `uv run pytest -q -m "not live"`.
- Run `uv build` when packaging or included documentation changes.
- Run `git diff --check` before handoff.
- Run focused tests first for fast feedback.
- Run the full non-live suite before completion.
- Do not replace a required gate with a weaker check.
- Report any skipped gate and the exact reason.

## Testing rules

- Add the smallest test that proves the contract.
- Test the observed case.
- Test one nearby boundary or negative case.
- Prefer public behavior over private implementation details.
- Keep contract fixtures deterministic.
- Keep write-safety regressions strict.
- Do not delete or weaken a failing test.
- Do not hide failures with broad skips.
- Mark real API tests with `live`.
- Ordinary CI must exclude live tests.
- Use official MCP clients for stdio integration proof.
- Verify the installed artifact, not only source imports.
- Verify supported Python versions through clean environments.
- Verify tool names as a set, not only a count.
- Verify zero overlap with mutating operations.

## Live-test safety

- Run live tests only with explicit authorization.
- Use a sacrificial Clockify workspace only.
- Confirm the reached workspace identity first.
- Resolve the current user through the API.
- Use one unique run prefix.
- Create prerequisites during the run.
- Capture every created entity ID.
- Clean exact created IDs in `finally`.
- Treat cleanup failure as an additional failure.
- Never mass-delete by a broad filter.
- Query the run prefix after cleanup.
- Require zero residue.
- Do not alter shared sacrificial infrastructure.

## Packaging

- Build with Hatchling through `uv build`.
- The wheel contains `clockify` and `clockify_mcp`.
- The core install must not require MCP.
- The `[mcp]` extra installs MCP dependencies.
- Keep the `clockify-mcp` console entry point.
- Inspect wheel and sdist contents for release work.
- Reject environment files and caches from artifacts.
- Keep required user and contributor documents in the sdist.
- Verify imports from an unrelated directory.
- Verify installed PEP 561 typing with a negative type check.
- Verify `clockify-mcp --help` keeps stdout clean.
- Verify stdio initialization from the installed package.

## Git and change scope

- Use small focused diffs.
- Edit only files required by the task.
- Do not stage unrelated changes.
- Do not use `git add -A` in a mixed worktree.
- Do not reset or discard user work.
- Do not force-push.
- Do not move published tags.
- Do not change CI, auth, or security settings unless asked.
- Do not commit or push unless the user authorizes it.
- Show the final changed-file scope.
- Keep commit messages short and specific when a commit is authorized.

## Release rules

- Use Trusted Publishing for PyPI.
- Do not use a PyPI API token for the trusted workflow.
- Keep metadata verification enabled.
- Pin GitHub Actions to commit objects.
- For annotated tags, pin the peeled commit when required.
- Keep publish-job OIDC permission least-privileged.
- Publish only verified artifacts from the successful build job.
- Verify public PyPI digests after publication.
- Verify GitHub release asset digests after upload.
- Verify clean public installs on Python 3.11 and 3.14.
- Never reuse an immutable version or tag.

## Final checklist

- Confirm the worktree state before editing.
- Confirm the current branch and HEAD.
- Confirm the task permits every intended mutation.
- Confirm no secret appears in the diff.
- Confirm protected headers remain blocked.
- Confirm host validation runs before credential attachment.
- Confirm redirects remain disabled.
- Confirm writes remain single-attempt.
- Confirm read retry tests cover both retry timing forms.
- Confirm operation IDs remain unique.
- Confirm resource-method pairs remain unique.
- Confirm all public methods are explicit.
