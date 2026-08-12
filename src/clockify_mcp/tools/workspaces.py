# pyright: reportUnusedFunction=false
"""Raw read tools: workspaces (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_workspaces_get", annotations=READ_ANNOTATIONS)
    async def clockify_workspaces_get(workspace_id: str | None = None) -> ReadResult:
        """Get one workspace's info and settings."""
        return await raw_read(
            client,
            "getWorkspaceInfo",
            path={"workspaceId": workspace_of(client, workspace_id)},
        )

    @server.tool(name="clockify_workspaces_list", annotations=READ_ANNOTATIONS)
    async def clockify_workspaces_list(roles: list[str] | None = None) -> ReadResult:
        """List all workspaces of the current user. No server-side paging: the
        full collection returns. `roles` is a repeated query key."""
        return await raw_read(client, "getAllMyWorkspaces", query={"roles": roles})
