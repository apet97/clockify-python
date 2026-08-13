"""MCP write-safety core.

Nothing in this package is imported by the read-only server
(`clockify_mcp.server`). The full server (`clockify_mcp.full_server`)
registers write tools through the shared runner: every guarded write passes
the sealed request-state gate described in docs/port/MCP_WRITE_SAFETY_PLAN.md.
"""
