# pyright: reportUnusedFunction=false
"""Guarded write tools: time off balance assignments."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import (
    CreateBalanceAssignmentV1Request,
    DeleteBalanceAssignmentV1Request,
    UpdateBalanceAssignmentV1Request,
)
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_time_off_balance_assignments_create",
        title="Create balance assignment",
        operation_id="createBalanceAssignment",
        body_model=CreateBalanceAssignmentV1Request,
    )

    async def prepare_create(
        body: CreateBalanceAssignmentV1Request, workspace_id: str | None = None
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
        name="clockify_time_off_balance_assignments_create",
        annotations=tool_annotations("clockify_time_off_balance_assignments_create"),
    )
    async def clockify_time_off_balance_assignments_create(
        body: CreateBalanceAssignmentV1Request,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a balance assignment for a user in a policy."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_time_off_balance_assignments_update",
        title="Update balance assignment",
        operation_id="updateBalanceAssignment",
        body_model=UpdateBalanceAssignmentV1Request,
    )

    async def prepare_update(
        balance_assignment_id: str,
        user_id: str,
        policy_id: str,
        body: UpdateBalanceAssignmentV1Request,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={
                "balance_assignment_id": balance_assignment_id,
                "user_id": user_id,
                "policy_id": policy_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update.workspace(workspace_id),
                "balanceAssignmentId": balance_assignment_id,
                "userId": user_id,
                "policyId": policy_id,
            },
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_balance_assignments_update",
        annotations=tool_annotations("clockify_time_off_balance_assignments_update"),
    )
    async def clockify_time_off_balance_assignments_update(
        balance_assignment_id: str,
        user_id: str,
        policy_id: str,
        body: UpdateBalanceAssignmentV1Request,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace a balance assignment (PUT)."""
        return await update.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_time_off_balance_assignments_delete",
        title="Delete balance assignment",
        operation_id="deleteBalanceAssignment",
        body_model=DeleteBalanceAssignmentV1Request,
    )

    async def prepare_delete(
        balance_assignment_id: str,
        user_id: str,
        policy_id: str,
        body: DeleteBalanceAssignmentV1Request,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await delete.prepare(
            arguments={
                "balance_assignment_id": balance_assignment_id,
                "user_id": user_id,
                "policy_id": policy_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": delete.workspace(workspace_id),
                "balanceAssignmentId": balance_assignment_id,
                "userId": user_id,
                "policyId": policy_id,
            },
            body=body,
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_balance_assignments_delete",
        annotations=tool_annotations("clockify_time_off_balance_assignments_delete"),
    )
    async def clockify_time_off_balance_assignments_delete(
        balance_assignment_id: str,
        user_id: str,
        policy_id: str,
        body: DeleteBalanceAssignmentV1Request,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a balance assignment. NOT reversible."""
        return await delete.run(prepared, approval)
