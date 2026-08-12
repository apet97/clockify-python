# Architecture

One distribution (`clockify-python-115`), two import packages.

```
                          Clockify API (3 hosts)
                                  │
                     HttpExecutor / one httpx.AsyncClient
                                  │
                   permanent operation registry (168 records)
                                  │
              ┌───────────────────┴───────────────────┐
        ClockifyClient                          MCP adapters
              │                                       │
     29 explicit resources               ┌────────────┴────────────┐
     reads and direct writes       ReadOnlyExecutor         write-safety gate
                                         │                  (not registered)
                                  60 read tools + 5 workflows
```

- `clockify.operations` — one frozen `Operation` record per endpoint, 29 domain
  modules, explicit `ALL_OPERATIONS`/`BY_ID`/`BY_PUBLIC_METHOD` in `registry.py`.
  The registry is the single runtime source of operation truth.
- `clockify.models` — static Pydantic v2 models generated once from the corrected
  OpenAPI by `scripts/import_openapi.py` and committed. Requests reject unknown
  fields; responses keep them in `model_extra`.
- `clockify._transport` — pure request compilation (`encode.py`), decoding
  (`decode.py`), final-host validation before credential attach (`hosts.py`),
  the executor with the read-only retry boundary, and `ReadOnlyExecutor`.
- `clockify.resources` — 29 explicit resource classes; one async method per
  operation; no runtime generation.
- `clockify_mcp` — read-only MCP server (`clockify-mcp` over stdio): 60 raw read
  tools + 5 workflows, every call through `ReadOnlyExecutor`.
- `clockify_mcp.writes` — the write-safety core (plan/nonce/gate/executor). It is
  structurally unreachable from the read server and registers no tools.

Dependency direction is one-way: models/operations → transport → resources/client
→ MCP read → MCP write. The SDK never imports `clockify_mcp`.
