# Changelog

## 0.1.1 (2026-08-13)

- Bound request authorization, retry behavior, and decoding to registered operations.
- Rejected unsafe injected HTTP client defaults before credentials or network access.
- Required HTTPS destinations and exact service-path containment.
- Redacted and bounded transport, API, and response-validation errors.
- Treated cancellation during write dispatch as an unknown mutation outcome.
- Enforced required query parameters, corrected public query types, and rejected
  unknown fields in nested request models.
- Corrected half-even money conversion and generated `_id` response fields.
- Added a response-aware pagination constructor that preserves `Last-Page`.
- Corrected MCP workspace fallbacks, date validation, result wording, and the final
  dormant-write precondition check.
- Kept the default MCP server at 65 read-only tools and zero writes.

## 0.1.0 (2026-08-12)

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
