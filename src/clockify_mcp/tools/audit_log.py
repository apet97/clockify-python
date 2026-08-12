# pyright: reportUnusedFunction=false
"""Raw read tools: audit_log (1 read)."""

from typing import Any

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_audit_log_search", annotations=READ_ANNOTATIONS)
    async def clockify_audit_log_search(
        workspace_id: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> ReadResult:
        """Search the workspace audit log (non-mutating POST on the audit-log host).
        `body` is an AuditLogRequest search filter; its action vocabulary is a closed
        enum — an invented action fails the request instead of matching nothing."""
        return await raw_read(
            client,
            "searchAuditLogs",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )
