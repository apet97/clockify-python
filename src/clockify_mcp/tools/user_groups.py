# pyright: reportUnusedFunction=false
"""Raw read tools: user_groups (1 read)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_user_groups_list", annotations=READ_ANNOTATIONS)
    async def clockify_user_groups_list(
        workspace_id: str | None = None,
        project_id: str | None = None,
        name: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        include_team_managers: bool | None = None,
    ) -> ReadResult:
        """List user groups on the workspace, filterable by name or project."""
        return await raw_read(
            client,
            "findAllGroupsOnWorkspace",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "project_id": project_id,
                "name": name,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
                "include_team_managers": include_team_managers,
            },
        )
