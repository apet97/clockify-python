# MCP guide

Install `clockify-python-115[mcp]` and run `clockify-mcp` over stdio.

The server exposes exactly 65 tools: 60 raw reads and five workflows. It
registers zero writes. Receipt download and invoice export remain SDK-only.
Public shared-report view accepts JSON or CSV and rejects PDF or XLSX before
network access.

Every raw tool and workflow uses `ReadOnlyExecutor`. Tool annotations describe
intent but do not enforce it. The executor is the final boundary.

Use `examples/mcp_config.example.json` as a shape example. Do not store a
credential in that file. Configure it through the host environment or a secret
store.

Logs go to stderr. Stdout contains MCP protocol traffic only.
