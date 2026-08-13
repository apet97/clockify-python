# pyright: reportUnusedFunction=false
"""Guarded write tools: time off balances."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import UpdateBalanceRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    update_for_policy = GuardedOp(
        deps,
        tool_name="clockify_time_off_balances_update_for_policy",
        title="Update time-off balances",
        operation_id="updateBalance",
        body_model=UpdateBalanceRequest,
    )

    async def prepare_update_for_policy(
        policy_id: str, body: UpdateBalanceRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_for_policy.prepare(
            arguments={"policy_id": policy_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": update_for_policy.workspace(workspace_id),
                "policyId": policy_id,
            },
            body=body,
        )

    def ask_update_for_policy(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_for_policy)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_balances_update_for_policy",
        annotations=tool_annotations("clockify_time_off_balances_update_for_policy"),
    )
    async def clockify_time_off_balances_update_for_policy(
        policy_id: str,
        body: UpdateBalanceRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_for_policy)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_for_policy)],
    ) -> WriteResult:
        """Adjust users' balances for a policy."""
        return await update_for_policy.run(prepared, approval)
