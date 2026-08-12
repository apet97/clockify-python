# pyright: reportUnusedFunction=false
"""Raw read tools: custom_fields (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_custom_fields_list_for_workspace", annotations=READ_ANNOTATIONS)
    async def clockify_custom_fields_list_for_workspace(
        workspace_id: str | None = None,
        name: str | None = None,
        status: str | None = None,
        entity_type: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List workspace-level custom fields. `page_size` max 200; the Last-Page
        header drives pagination."""
        return await raw_read(
            client,
            "listWorkspaceCustomFields",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "name": name,
                "status": status,
                "entity_type": entity_type,
                "page": page,
                "page_size": page_size,
            },
        )

    @server.tool(name="clockify_custom_fields_list_for_project", annotations=READ_ANNOTATIONS)
    async def clockify_custom_fields_list_for_project(
        project_id: str,
        workspace_id: str | None = None,
        status: str | None = None,
        entity_type: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List custom fields configured on one project. `page_size` max 200."""
        return await raw_read(
            client,
            "listProjectCustomFields",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "projectId": project_id,
            },
            query={
                "status": status,
                "entity_type": entity_type,
                "page": page,
                "page_size": page_size,
            },
        )
