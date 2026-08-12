# Changelog

## 0.1.0 (unreleased)

Initial implementation:

- complete async SDK: 168 operations, 29 resources, static Pydantic v2 models
- multi-host executor with final-host validation, no-redirect, read-only retry
- pagination/money helpers and known-deviation regression suite
- read-only MCP server: 60 raw read tools + 5 workflows over stdio
- MCP write-safety core (plan/nonce/gate/controlled executor); no write tools
  registered
