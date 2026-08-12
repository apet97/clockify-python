# Phase 6 raw-read-tool template (internal working note; deleted after Phase 6)

Implement `src/clockify_mcp/tools/<resource>.py` for each assigned resource, following
the exemplar `src/clockify_mcp/tools/tags.py` exactly (read it plus
`src/clockify_mcp/tools/_shared.py` first).

Rules:

- One module per resource with a single `def register(server: MCPServer, client: ClockifyClient) -> None:`
  containing one `@server.tool(name="clockify_<resource>_<method>", annotations=READ_ANNOTATIONS)`
  async function per ELIGIBLE read operation of that resource (the assignment lists them).
- Tool function name == tool name. Parameters:
  - path params (other than workspaceId) as required `str` args, snake_case;
  - `workspace_id: str | None = None` when the path has {workspaceId}, resolved via
    `workspace_of(client, workspace_id)`; omit entirely when the path has no workspaceId;
  - query params keyword-style with `None` defaults, exactly the python_names from the
    Operation record in `src/clockify/operations/<resource>.py` (the raw executor
    validates them, so names must match);
  - JSON-body POST reads take `body: dict[str, Any] | None = None` (or a required dict
    when the operation requires it) and pass it through — describe the body briefly in
    the docstring using the request model name from tests/fixtures/wiring/<resource>.json.
- Call `raw_read(client, "<operationId>", path=..., query=..., body=...)` and return it.
- Docstring: one or two sentences an agent needs (what it returns, key filters, hazards
  from the wiring fixture notes). No essays.
- SPECIAL CASE `shared_reports.view_public` (`getSharedReportsSharedReportId`):
  it is content-negotiated. The tool must accept `format: str = "JSON"`, uppercase it,
  reject anything except JSON or CSV by raising
  `ToolError("format must be JSON or CSV; PDF/XLSX are SDK-only")` BEFORE any network
  call, and send it as the proper query/header per the Operation record. Import ToolError
  from clockify_mcp.errors.
- Do not import anything from clockify_mcp.writes (does not exist) and do not add tools
  for mutating or binary operations.

Verify:

```bash
cd /Users/15x/Downloads/WORKING/addons-me/2mcp
uv run python -c "import clockify_mcp.tools.<each>"
uv run ruff check src/clockify_mcp && uv run pyright src/clockify_mcp 2>&1 | tail -1
```

Return the tool counts per module.
