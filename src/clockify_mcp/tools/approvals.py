# pyright: reportUnusedFunction=false
"""Raw read tools: approvals (1 read)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_approvals_list", annotations=READ_ANNOTATIONS)
    async def clockify_approvals_list(
        workspace_id: str | None = None,
        status: str | None = None,
        sort_column: str | None = None,
        types: list[str] | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List approval requests. Filter by `status` and `types`; the Last-Page header
        drives pagination. userId and date filters are ignored by the live API."""
        return await raw_read(
            client,
            "getApprovalRequests",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "status": status,
                "sort_column": sort_column,
                "types": types,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )
