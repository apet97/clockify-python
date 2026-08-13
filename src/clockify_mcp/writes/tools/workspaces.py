# pyright: reportUnusedFunction=false
"""Guarded write tools: workspaces."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import UpdateCostRateRequest, UpdateWorkspaceBillableRateRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    update_billable_rate = GuardedOp(
        deps,
        tool_name="clockify_workspaces_update_billable_rate",
        title="Update workspace billable rate",
        operation_id="updateWorkspaceBillableRate",
        body_model=UpdateWorkspaceBillableRateRequest,
    )

    async def prepare_update_billable_rate(
        body: UpdateWorkspaceBillableRateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_billable_rate.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update_billable_rate.workspace(workspace_id)},
            body=body,
        )

    def ask_update_billable_rate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_billable_rate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_workspaces_update_billable_rate",
        annotations=tool_annotations("clockify_workspaces_update_billable_rate"),
    )
    async def clockify_workspaces_update_billable_rate(
        body: UpdateWorkspaceBillableRateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_billable_rate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_billable_rate)],
    ) -> WriteResult:
        """Set the workspace default billable rate."""
        return await update_billable_rate.run(prepared, approval)

    update_cost_rate = GuardedOp(
        deps,
        tool_name="clockify_workspaces_update_cost_rate",
        title="Update workspace cost rate",
        operation_id="updateWorkspaceCostRate",
        body_model=UpdateCostRateRequest,
    )

    async def prepare_update_cost_rate(
        body: UpdateCostRateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_cost_rate.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update_cost_rate.workspace(workspace_id)},
            body=body,
        )

    def ask_update_cost_rate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_cost_rate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_workspaces_update_cost_rate",
        annotations=tool_annotations("clockify_workspaces_update_cost_rate"),
    )
    async def clockify_workspaces_update_cost_rate(
        body: UpdateCostRateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_cost_rate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_cost_rate)],
    ) -> WriteResult:
        """Set the workspace default cost rate."""
        return await update_cost_rate.run(prepared, approval)
