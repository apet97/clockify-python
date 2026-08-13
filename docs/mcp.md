# Clockify MCP server

Read-only MCP server over stdio.

```bash
uv add "clockify-python-115[mcp]"
clockify-mcp            # or: python -m clockify_mcp
```

Environment: exactly one of `CLOCKIFY_API_KEY` or `CLOCKIFY_ADDON_TOKEN`, plus
optional `CLOCKIFY_WORKSPACE_ID` (otherwise tools fall back to the user's
default workspace).

Client configuration example (`examples/mcp_config.example.json` has the same
shape; never store a credential in that file — supply it through the host
environment or a secret store):

```json
{
  "mcpServers": {
    "clockify": {
      "command": "clockify-mcp",
      "env": {"CLOCKIFY_API_KEY": "…", "CLOCKIFY_WORKSPACE_ID": "…"}
    }
  }
}
```

## Tools

- 60 raw read tools named `clockify_<resource>_<method>`, mirroring the SDK's
  non-mutating operations. Two binary reads (receipt download, invoice export)
  are SDK-only. Public shared-report view accepts JSON/CSV only.
- 5 workflows: `clockify_status`, `clockify_workspace_overview`,
  `clockify_review_day`, `clockify_review_week`, `clockify_doctor`.

## Write support

None. The server is structurally read-only: every call passes a final
`ReadOnlyExecutor` boundary that refuses mutating operations before any HTTP
request. Tool annotations describe intent but do not enforce it; the executor
is the enforcement. A write-safety core exists (`clockify_mcp.writes`) but registers no
tools; writes ship only when every condition in
`docs/port/MCP_WRITE_SAFETY_PLAN.md` is proven, including real target-host
approval-UI evidence and independent review.

Logs go to stderr; stdout carries only MCP protocol traffic.
