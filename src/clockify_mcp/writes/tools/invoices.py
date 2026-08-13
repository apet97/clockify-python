# pyright: reportUnusedFunction=false
"""Guarded write tools: invoices."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import InvoiceCreateRequest, InvoiceStatusRequest, UpdateInvoiceRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_invoices_create",
        title="Create invoice",
        operation_id="addInvoice",
        body_model=InvoiceCreateRequest,
    )

    async def prepare_create(
        body: InvoiceCreateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await create.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": create.workspace(workspace_id)},
            body=body,
        )

    def ask_create(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoices_create", annotations=tool_annotations("clockify_invoices_create")
    )
    async def clockify_invoices_create(
        body: InvoiceCreateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create an invoice."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_invoices_update",
        title="Update invoice",
        operation_id="updateInvoice",
        body_model=UpdateInvoiceRequest,
    )

    async def prepare_update(
        invoice_id: str, body: UpdateInvoiceRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={"invoice_id": invoice_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id), "invoiceId": invoice_id},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoices_update", annotations=tool_annotations("clockify_invoices_update")
    )
    async def clockify_invoices_update(
        invoice_id: str,
        body: UpdateInvoiceRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace an invoice (PUT: send every field you want to keep)."""
        return await update.run(prepared, approval)

    update_status = GuardedOp(
        deps,
        tool_name="clockify_invoices_update_status",
        title="Change invoice status",
        operation_id="changeInvoiceStatus",
        body_model=InvoiceStatusRequest,
    )

    async def prepare_update_status(
        invoice_id: str, body: InvoiceStatusRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_status.prepare(
            arguments={"invoice_id": invoice_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": update_status.workspace(workspace_id),
                "invoiceId": invoice_id,
            },
            body=body,
        )

    def ask_update_status(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoices_update_status",
        annotations=tool_annotations("clockify_invoices_update_status"),
    )
    async def clockify_invoices_update_status(
        invoice_id: str,
        body: InvoiceStatusRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_status)],
    ) -> WriteResult:
        """Change an invoice's status."""
        return await update_status.run(prepared, approval)

    duplicate = GuardedOp(
        deps,
        tool_name="clockify_invoices_duplicate",
        title="Duplicate invoice",
        operation_id="duplicateInvoice",
    )

    async def prepare_duplicate(invoice_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await duplicate.prepare(
            arguments={"invoice_id": invoice_id, "workspace_id": workspace_id},
            path_args={"workspaceId": duplicate.workspace(workspace_id), "invoiceId": invoice_id},
        )

    def ask_duplicate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_duplicate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoices_duplicate",
        annotations=tool_annotations("clockify_invoices_duplicate"),
    )
    async def clockify_invoices_duplicate(
        invoice_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_duplicate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_duplicate)],
    ) -> WriteResult:
        """Duplicate an invoice."""
        return await duplicate.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_invoices_delete",
        title="Delete invoice",
        operation_id="deleteInvoice",
    )

    async def prepare_delete(invoice_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"invoice_id": invoice_id, "workspace_id": workspace_id},
            path_args={"workspaceId": delete.workspace(workspace_id), "invoiceId": invoice_id},
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoices_delete", annotations=tool_annotations("clockify_invoices_delete")
    )
    async def clockify_invoices_delete(
        invoice_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete an invoice. NOT reversible."""
        return await delete.run(prepared, approval)
