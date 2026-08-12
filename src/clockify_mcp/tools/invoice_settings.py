# pyright: reportUnusedFunction=false
"""Raw read tools: invoice_settings (1 read)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_invoice_settings_get", annotations=READ_ANNOTATIONS)
    async def clockify_invoice_settings_get(workspace_id: str | None = None) -> ReadResult:
        """Get workspace-wide invoice settings (defaults applied to new invoices)."""
        return await raw_read(
            client,
            "getInvoiceSettings",
            path={"workspaceId": workspace_of(client, workspace_id)},
        )
