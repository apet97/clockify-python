# pyright: reportUnusedFunction=false
"""Guarded write tools: invoice items."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import AddInvoiceItemRequest, ImportInvoiceItemsRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_invoice_items_create",
        title="Add invoice item",
        operation_id="addInvoiceItem",
        body_model=AddInvoiceItemRequest,
    )

    async def prepare_create(
        invoice_id: str, body: AddInvoiceItemRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await create.prepare(
            arguments={"invoice_id": invoice_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": create.workspace(workspace_id), "invoiceId": invoice_id},
            body=body,
        )

    def ask_create(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoice_items_create",
        annotations=tool_annotations("clockify_invoice_items_create"),
    )
    async def clockify_invoice_items_create(
        invoice_id: str,
        body: AddInvoiceItemRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Add an item to an invoice."""
        return await create.run(prepared, approval)

    import_items = GuardedOp(
        deps,
        tool_name="clockify_invoice_items_import_items",
        title="Import invoice items",
        operation_id="importInvoiceItems",
        body_model=ImportInvoiceItemsRequest,
    )

    async def prepare_import_items(
        invoice_id: str, body: ImportInvoiceItemsRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await import_items.prepare(
            arguments={"invoice_id": invoice_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": import_items.workspace(workspace_id),
                "invoiceId": invoice_id,
            },
            body=body,
        )

    def ask_import_items(
        prepared: Annotated[PreparedWrite, Resolve(prepare_import_items)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoice_items_import_items",
        annotations=tool_annotations("clockify_invoice_items_import_items"),
    )
    async def clockify_invoice_items_import_items(
        invoice_id: str,
        body: ImportInvoiceItemsRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_import_items)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_import_items)],
    ) -> WriteResult:
        """Import time entries and expenses into an invoice."""
        return await import_items.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_invoice_items_delete",
        title="Delete invoice item",
        operation_id="deleteInvoiceItem",
    )

    async def prepare_delete(
        invoice_id: str, order: int, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await delete.prepare(
            arguments={"invoice_id": invoice_id, "order": order, "workspace_id": workspace_id},
            path_args={
                "workspaceId": delete.workspace(workspace_id),
                "invoiceId": invoice_id,
                "order": str(order),
            },
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoice_items_delete",
        annotations=tool_annotations("clockify_invoice_items_delete"),
    )
    async def clockify_invoice_items_delete(
        invoice_id: str,
        order: int,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete an invoice item by its order index. NOT reversible."""
        return await delete.run(prepared, approval)
