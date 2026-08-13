# pyright: reportUnusedFunction=false
"""Guarded write tools: invoice payments."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import AddInvoicePaymentRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_invoice_payments_create",
        title="Add invoice payment",
        operation_id="addInvoicePayment",
        body_model=AddInvoicePaymentRequest,
    )

    async def prepare_create(
        invoice_id: str, body: AddInvoicePaymentRequest, workspace_id: str | None = None
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
        name="clockify_invoice_payments_create",
        annotations=tool_annotations("clockify_invoice_payments_create"),
    )
    async def clockify_invoice_payments_create(
        invoice_id: str,
        body: AddInvoicePaymentRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Add a payment to an invoice. The response is the updated invoice."""
        return await create.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_invoice_payments_delete",
        title="Delete invoice payment",
        operation_id="deleteInvoicePayment",
    )

    async def prepare_delete(
        invoice_id: str, payment_id: str, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await delete.prepare(
            arguments={
                "invoice_id": invoice_id,
                "payment_id": payment_id,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": delete.workspace(workspace_id),
                "invoiceId": invoice_id,
                "paymentId": payment_id,
            },
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoice_payments_delete",
        annotations=tool_annotations("clockify_invoice_payments_delete"),
    )
    async def clockify_invoice_payments_delete(
        invoice_id: str,
        payment_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a payment from an invoice. NOT reversible."""
        return await delete.run(prepared, approval)
