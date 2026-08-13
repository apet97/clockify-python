# pyright: reportUnusedFunction=false
"""Raw read tools: tags (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_tags_list", annotations=READ_ANNOTATIONS)
    async def clockify_tags_list(
        workspace_id: str | None = None,
        name: str | None = None,
        strict_name_search: bool | None = None,
        excluded_ids: str | None = None,
        archived: bool | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List workspace tags. Omitting `archived` returns archived AND active tags."""
        return await raw_read(
            client,
            "getWorkspacesWorkspaceIdTags",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "name": name,
                "strict_name_search": strict_name_search,
                "excluded_ids": excluded_ids,
                "archived": archived,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )

    @server.tool(name="clockify_tags_get", annotations=READ_ANNOTATIONS)
    async def clockify_tags_get(tag_id: str, workspace_id: str | None = None) -> ReadResult:
        """Get one tag by ID."""
        return await raw_read(
            client,
            "getWorkspacesWorkspaceIdTagsTagId",
            path={"workspaceId": workspace_of(client, workspace_id), "tagId": tag_id},
        )
