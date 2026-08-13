# pyright: reportUnusedFunction=false
"""Guarded write tools: time off policies."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import (
    CreateTimeOffPolicyRequest,
    PolicyStatusChangeRequest,
    UpdateTimeOffPolicyRequest,
)
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_time_off_policies_create",
        title="Create time-off policy",
        operation_id="createTimeOffPolicy",
        body_model=CreateTimeOffPolicyRequest,
    )

    async def prepare_create(
        body: CreateTimeOffPolicyRequest, workspace_id: str | None = None
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
        name="clockify_time_off_policies_create",
        annotations=tool_annotations("clockify_time_off_policies_create"),
    )
    async def clockify_time_off_policies_create(
        body: CreateTimeOffPolicyRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a time-off policy."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_time_off_policies_update",
        title="Update time-off policy",
        operation_id="updateTimeOffPolicy",
        body_model=UpdateTimeOffPolicyRequest,
    )

    async def prepare_update(
        policy_id: str, body: UpdateTimeOffPolicyRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={"policy_id": policy_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id), "policyId": policy_id},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_policies_update",
        annotations=tool_annotations("clockify_time_off_policies_update"),
    )
    async def clockify_time_off_policies_update(
        policy_id: str,
        body: UpdateTimeOffPolicyRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace a time-off policy (PUT)."""
        return await update.run(prepared, approval)

    update_status = GuardedOp(
        deps,
        tool_name="clockify_time_off_policies_update_status",
        title="Change policy status",
        operation_id="changeTimeOffPolicyStatus",
        body_model=PolicyStatusChangeRequest,
    )

    async def prepare_update_status(
        policy_id: str, body: PolicyStatusChangeRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_status.prepare(
            arguments={"policy_id": policy_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update_status.workspace(workspace_id), "policyId": policy_id},
            body=body,
        )

    def ask_update_status(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_policies_update_status",
        annotations=tool_annotations("clockify_time_off_policies_update_status"),
    )
    async def clockify_time_off_policies_update_status(
        policy_id: str,
        body: PolicyStatusChangeRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_status)],
    ) -> WriteResult:
        """Archive or activate a time-off policy."""
        return await update_status.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_time_off_policies_delete",
        title="Delete time-off policy",
        operation_id="deleteTimeOffPolicy",
    )

    async def prepare_delete(policy_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"policy_id": policy_id, "workspace_id": workspace_id},
            path_args={"workspaceId": delete.workspace(workspace_id), "policyId": policy_id},
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_policies_delete",
        annotations=tool_annotations("clockify_time_off_policies_delete"),
    )
    async def clockify_time_off_policies_delete(
        policy_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a time-off policy. NOT reversible."""
        return await delete.run(prepared, approval)
