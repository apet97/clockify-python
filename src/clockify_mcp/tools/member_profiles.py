# pyright: reportUnusedFunction=false
"""Raw read tools: member_profiles (1 read)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_member_profiles_get", annotations=READ_ANNOTATIONS)
    async def clockify_member_profiles_get(
        user_id: str, workspace_id: str | None = None
    ) -> ReadResult:
        """Get one workspace member's profile (MemberProfileDtoV1) by user ID."""
        return await raw_read(
            client,
            "getMemberProfile",
            path={"workspaceId": workspace_of(client, workspace_id), "userId": user_id},
        )
