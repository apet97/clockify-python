# Security

- The SDK sends exactly one Clockify credential (`X-Api-Key` or `X-Addon-Token`),
  attached only after the final destination host is validated. Redirects are never
  followed.
- Credentials never appear in `repr`, exceptions, logs, or MCP output.
- The MCP server ships structurally read-only. Write tools are gated by the plan in
  `docs/port/MCP_WRITE_SAFETY_PLAN.md` and are not registered by default.
- Report vulnerabilities through a private GitHub security advisory on this repository.
