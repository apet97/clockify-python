# pyright: reportUnusedFunction=false
"""Raw read tools: clients (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_clients_list", annotations=READ_ANNOTATIONS)
    async def clockify_clients_list(
        workspace_id: str | None = None,
        name: str | None = None,
        archived: bool | None = None,
        address: str | None = None,
        note: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List workspace clients. Omitting `archived` returns archived AND active clients."""
        return await raw_read(
            client,
            "getWorkspacesWorkspaceIdClients",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "name": name,
                "archived": archived,
                "address": address,
                "note": note,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )

    @server.tool(name="clockify_clients_get", annotations=READ_ANNOTATIONS)
    async def clockify_clients_get(client_id: str, workspace_id: str | None = None) -> ReadResult:
        """Get one client by ID."""
        return await raw_read(
            client,
            "getWorkspacesWorkspaceIdClientsClientId",
            path={"workspaceId": workspace_of(client, workspace_id), "clientId": client_id},
        )
