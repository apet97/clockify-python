# pyright: reportUnusedFunction=false
"""Raw read tools: time_off_requests (1 read)."""

from typing import Any

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_time_off_requests_list", annotations=READ_ANNOTATIONS)
    async def clockify_time_off_requests_list(
        workspace_id: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> ReadResult:
        """List time-off requests on the workspace (non-mutating search POST).
        `body` is a TimeOffRequestSearchRequest filter; items arrive under the
        `requests` envelope key."""
        return await raw_read(
            client,
            "getAllTimeOffRequestsOnWorkspace",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )
