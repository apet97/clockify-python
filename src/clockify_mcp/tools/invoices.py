# pyright: reportUnusedFunction=false
"""Raw read tools: invoices (3 reads; export is binary and SDK-only)."""

from typing import Any

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_invoices_list", annotations=READ_ANNOTATIONS)
    async def clockify_invoices_list(
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        statuses: list[str] | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
    ) -> ReadResult:
        """List workspace invoices (items under `invoices`). Money fields are MINOR
        units (cents); the Last-Page header drives pagination."""
        return await raw_read(
            client,
            "getWorkspaceInvoices",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "page": page,
                "page_size": page_size,
                "statuses": statuses,
                "sort_column": sort_column,
                "sort_order": sort_order,
            },
        )

    @server.tool(name="clockify_invoices_get", annotations=READ_ANNOTATIONS)
    async def clockify_invoices_get(invoice_id: str, workspace_id: str | None = None) -> ReadResult:
        """Get one invoice by ID. A deleted or unknown id answers 400 code 501
        ("Invoice doesn't belong to Workspace"), never 404."""
        return await raw_read(
            client,
            "getInvoiceById",
            path={"workspaceId": workspace_of(client, workspace_id), "invoiceId": invoice_id},
        )

    @server.tool(name="clockify_invoices_filter", annotations=READ_ANNOTATIONS)
    async def clockify_invoices_filter(
        workspace_id: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> ReadResult:
        """Filter invoices (non-mutating POST; the JSON `body` is an
        InvoiceFilterRequest search filter). Matching items come back under `invoices`."""
        return await raw_read(
            client,
            "filterInvoices",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )
