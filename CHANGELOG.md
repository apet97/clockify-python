# Changelog

## 0.1.0 (unreleased)

- Added a typed async SDK with 168 explicit operations and 29 resources.
- Added static Pydantic v2 models for 339 reachable schema roots.
- Added regular, reports, and audit-log host routing.
- Added JSON, multipart, text, binary, empty, and negotiated response handling.
- Added bounded sanitized API errors and protected authenticated headers.
- Added read retries with delay-seconds and HTTP-date `Retry-After` support.
- Added PEP 561 markers for `clockify` and `clockify_mcp`.
- Added a read-only MCP server with 60 raw tools and five workflows.
- Kept all MCP writes unregistered. The internal write-safety core remains dormant.
- Documented conservative replacement semantics and independent project status.
