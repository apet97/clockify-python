# pyright: reportUnusedFunction=false
"""Guarded write tools: invoice settings."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import InvoiceSettingsRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    update = GuardedOp(
        deps,
        tool_name="clockify_invoice_settings_update",
        title="Update invoice settings",
        operation_id="updateInvoiceSettings",
        body_model=InvoiceSettingsRequest,
    )

    async def prepare_update(
        body: InvoiceSettingsRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id)},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoice_settings_update",
        annotations=tool_annotations("clockify_invoice_settings_update"),
    )
    async def clockify_invoice_settings_update(
        body: InvoiceSettingsRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace workspace invoice settings (PUT)."""
        return await update.run(prepared, approval)
