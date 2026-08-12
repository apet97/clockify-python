# pyright: reportUnusedFunction=false
"""Raw read tools: invoice_payments (1 read)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_invoice_payments_list", annotations=READ_ANNOTATIONS)
    async def clockify_invoice_payments_list(
        invoice_id: str,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List payments on one invoice (bare array). Item `amount` is MINOR units
        (cents); items use `date`, not the request-side `paymentDate`."""
        return await raw_read(
            client,
            "getInvoicePayments",
            path={"workspaceId": workspace_of(client, workspace_id), "invoiceId": invoice_id},
            query={"page": page, "page_size": page_size},
        )
