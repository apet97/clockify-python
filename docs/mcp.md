# Clockify MCP server

Full-featured MCP server. stdio by default; Streamable HTTP with `--http`.

```bash
uv add "clockify-python-115[mcp]"
clockify-mcp                              # stdio (default)
clockify-mcp --http --host 127.0.0.1 --port 8000
python -m clockify_mcp                    # same as clockify-mcp
```

Environment: exactly one of `CLOCKIFY_API_KEY` or `CLOCKIFY_ADDON_TOKEN`, plus
optional `CLOCKIFY_WORKSPACE_ID` (otherwise tools fall back to the user's
default workspace). `CLOCKIFY_MCP_READ_ONLY=true` serves the structurally
read-only build: 65 tools, zero writes, no write code imported.

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

## Tools (186)

- 60 raw read tools named `clockify_<resource>_<method>`, mirroring the SDK's
  non-mutating operations. Two binary reads (receipt download, invoice export)
  are SDK-only. Public shared-report view accepts JSON/CSV only.
- 104 raw write tools covering every mutating operation except binary file
  upload and workspace creation. Expense create/update ship without file
  attachments.
- 18 workflows: 5 read (`clockify_status`, `clockify_workspace_overview`,
  `clockify_review_day`, `clockify_review_week`, `clockify_doctor`), 7 routine
  write (`clockify_start_work`, `clockify_stop_work`, `clockify_switch_work`,
  `clockify_log_work`, `clockify_fix_entry`, `clockify_create_work_package`,
  `clockify_demo_seed`), and 6 gated write (`clockify_invoice_client_work`,
  `clockify_record_expense`, `clockify_request_time_off`,
  `clockify_schedule_work`, `clockify_setup_webhook`,
  `clockify_demo_cleanup`).
- 4 orientation tools (`clockify_tools_guide`, `clockify_plan_change`,
  `clockify_operation_guide`, `clockify_sdk_snippet`), 6 `clockify://` guide
  resources, and 2 prompts.

## Write safety

Two tiers, decided per tool in `clockify_mcp.risk`:

- **Routine** (personal time entries, daily-tracking workflows): executes
  directly, single attempt, never retried.
- **Guarded** (business, external side effect, privileged, destructive): the
  server compiles the exact wire request into a plan, shows the user a
  deterministic preview, and waits for approval through the MCP sealed
  request-state mechanism (spec 2026-07-28 round trips; legacy elicitation on
  older hosts). The approval is invisible to the model. A single-use
  confirmation binds the exact plan bytes: argument or state drift after
  approval refuses the write, replays fail closed, and only the stored plan
  ever dispatches. Hosts without approval support cannot execute guarded
  writes.

Failure states are explicit: `rejected`, `failed_before_dispatch`, `failed`,
`partial_failure` (multi-step plans report exactly which steps applied),
`outcome_unknown` (ambiguous transport failure — read state before any manual
retry), `succeeded`, and `reconciled`.

Webhook tools validate target URLs offline (HTTPS only, no private or
metadata destinations) and redact the returned `authToken`.
`clockify_demo_cleanup` only ever deletes `DEMO-`/`sdk-demo-` prefixed
entities, under one approval that lists every deletion.

The read boundary is unchanged: every read tool passes `ReadOnlyExecutor`,
which refuses mutating operations before any HTTP request. Tool annotations
describe intent but do not enforce it.

Logs go to stderr; stdout carries only MCP protocol traffic in stdio mode.
