# Phase 4 resource-module template (internal working note; deleted after Phase 4)

Implement `src/clockify/resources/<resource>.py` plus
`tests/contract/wiring/test_wiring_<resource>.py` for each assigned resource.

Canonical style exemplars (read them first, follow them exactly):
- `src/clockify/resources/tags.py`
- `tests/contract/wiring/test_wiring_tags.py`
- shared plumbing: `src/clockify/resources/_base.py`
- test harness: `tests/contract/wiring/_harness.py`

Authoritative inputs per operation:
- `src/clockify/operations/<resource>.py` — the Operation constants (already verified).
- `tests/fixtures/wiring/<resource>.json` — request/response model names + notes.
- `docs/port/OPERATION_PORT_MANIFEST.md` — only when the fixture notes are unclear.
- `src/clockify/models/__init__.py` `__all__` — the model class names that exist.

## Resource module rules

- `class <ResourcePascal>Resource(ResourceBase)`; one `async def` per operation,
  named exactly `Operation.sdk_method`.
- Path parameters (other than `workspaceId`) are positional `str` arguments, in path
  order, named snake_case of the wire name (`tagId` -> `tag_id`).
- Operations whose path contains `{workspaceId}` take keyword-only
  `workspace_id: str | None = None` and resolve via `self._workspace(workspace_id)`.
  Operations without it (e.g. `users.me`, `workspaces.list`, `shared_reports.view_public`)
  take no workspace argument.
- JSON body operations: parameter `body: <RequestModel> | Mapping[str, Any]`, validated
  with `self._coerce(body, <RequestModel>)`. When the fixture says the body is an inline
  schema with no component model (`request_model: null` + note), accept
  `body: Mapping[str, Any]` and pass `dict(body)` through (see `tags.update`); if the body
  is optional per the manifest, make it `body: Mapping[str, Any] | None = None`.
- Query parameters: keyword-only, python names from the QueryParameter records, all
  defaulting to `None`; pass a dict with every python_name to `_call(query=...)`.
  Type them: `str | None`, `int | None`, `bool | None`, `list[str] | None` per the record.
- Multipart operations: `file: Upload` (or optional) plus form fields; pass
  `files={"file": upload}` and `body=<mapping of form fields>`.
- Return types by fixture `response.shape`:
  - "model" -> the model class via `self._adapt(OP, response, Model)`
  - "list"  -> `list[Model]` via a module-level `TypeAdapter(list[Model])`
  - "none"  -> `None` (still `await self._call(...)`; return None)
  - "bytes" -> `BinaryResponse` (return `response.data`)
  - "text"  -> `TextResponse` (return `response.data`)
  - "negotiated" -> return `response.data` typed `Any` (docstring states the variants)
  - envelope lists where the envelope has a component model -> return the envelope model.
- One-line docstrings only where the fixture notes carry a real hazard (lifecycle
  prerequisite, replacement risk, money unit, weird envelope, payment-ID recovery).
  No prose essays; no repetition of the OpenAPI description.

## Wiring test rules

- File starts with `COVERED = {<operation_id>, ...}` listing every operation in the module.
- Use `make_client(...)` + `assert_wired(...)` from `_harness`; one test per operation
  minimum, asserting: exact URL (host + rendered path), HTTP method (via assert_wired),
  query wire names for every query parameter at least once per operation that has them,
  exact body JSON for body operations, and the adapted return type.
- For bytes/text/negotiated responses use `make_client(content=..., content_type=...)`.
- Response sample JSON must satisfy the response model's required fields — check the model
  in `src/clockify/models/` and keep samples minimal.
- Test workspace default fallback at least once per module (no explicit workspace_id).

## Verification each agent must run

```bash
cd /Users/15x/Downloads/WORKING/addons-me/2mcp
uv run python -c "import clockify.resources.<each_module>"
uv run pytest -q tests/contract/wiring/test_wiring_<each_resource>.py  # will fail with
# ModuleNotFoundError for OTHER resources via client.py until all agents finish — in that
# case verify with: uv run python -m pytest --collect-only -q <file> 2>&1 | head
```

If `clockify.client` import blocks your test run because other agents' modules are
missing, still make sure your module imports cleanly and your test file is complete;
the main thread runs the full suite at the end.
