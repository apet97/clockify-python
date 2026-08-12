# pyright: reportUnusedFunction=false
"""Raw read tools: expense_categories (1 read)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_expense_categories_list", annotations=READ_ANNOTATIONS)
    async def clockify_expense_categories_list(
        workspace_id: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        archived: bool | None = None,
        name: str | None = None,
    ) -> ReadResult:
        """List expense categories. Items are nested under a `categories` envelope;
        the Last-Page header drives pagination."""
        return await raw_read(
            client,
            "getExpenseCategories",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
                "archived": archived,
                "name": name,
            },
        )
