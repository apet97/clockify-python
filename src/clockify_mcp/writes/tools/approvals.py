# pyright: reportUnusedFunction=false
"""Guarded write tools: approvals."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import (
    CreateApprovalRequestNoType,
    SubmitApprovalRequestRequest,
    UpdateApprovalRequestRequest,
)
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    submit = GuardedOp(
        deps,
        tool_name="clockify_approvals_submit",
        title="Submit approval request",
        operation_id="submitApprovalRequest",
        body_model=SubmitApprovalRequestRequest,
    )

    async def prepare_submit(
        body: SubmitApprovalRequestRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await submit.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": submit.workspace(workspace_id)},
            body=body,
        )

    def ask_submit(
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_approvals_submit", annotations=tool_annotations("clockify_approvals_submit")
    )
    async def clockify_approvals_submit(
        body: SubmitApprovalRequestRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_submit)],
    ) -> WriteResult:
        """Submit the current user's pending entries for approval. Deprecated upstream; prefer submit_with_type."""
        return await submit.run(prepared, approval)

    submit_for_user = GuardedOp(
        deps,
        tool_name="clockify_approvals_submit_for_user",
        title="Submit approval for user",
        operation_id="submitApprovalRequestForUser",
        body_model=SubmitApprovalRequestRequest,
    )

    async def prepare_submit_for_user(
        user_id: str, body: SubmitApprovalRequestRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await submit_for_user.prepare(
            arguments={"user_id": user_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": submit_for_user.workspace(workspace_id), "userId": user_id},
            body=body,
        )

    def ask_submit_for_user(
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit_for_user)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_approvals_submit_for_user",
        annotations=tool_annotations("clockify_approvals_submit_for_user"),
    )
    async def clockify_approvals_submit_for_user(
        user_id: str,
        body: SubmitApprovalRequestRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit_for_user)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_submit_for_user)],
    ) -> WriteResult:
        """Submit a user's pending entries for approval. Deprecated upstream; prefer submit_for_user_with_type."""
        return await submit_for_user.run(prepared, approval)

    submit_with_type = GuardedOp(
        deps,
        tool_name="clockify_approvals_submit_with_type",
        title="Submit typed approval request",
        operation_id="createApprrovalRequest_1",
        body_model=CreateApprovalRequestNoType,
    )

    async def prepare_submit_with_type(
        approval_type: str, body: CreateApprovalRequestNoType, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await submit_with_type.prepare(
            arguments={"approval_type": approval_type, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": submit_with_type.workspace(workspace_id),
                "approvalRequestId": approval_type,
            },
            body=body,
        )

    def ask_submit_with_type(
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit_with_type)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_approvals_submit_with_type",
        annotations=tool_annotations("clockify_approvals_submit_with_type"),
    )
    async def clockify_approvals_submit_with_type(
        approval_type: str,
        body: CreateApprovalRequestNoType,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit_with_type)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_submit_with_type)],
    ) -> WriteResult:
        """Submit an approval request with a type. `approval_type` is TIMESHEET or EXPENSE."""
        return await submit_with_type.run(prepared, approval)

    submit_for_user_with_type = GuardedOp(
        deps,
        tool_name="clockify_approvals_submit_for_user_with_type",
        title="Submit typed approval for user",
        operation_id="createApprovalForOtherWithType",
        body_model=CreateApprovalRequestNoType,
    )

    async def prepare_submit_for_user_with_type(
        user_id: str,
        approval_type: str,
        body: CreateApprovalRequestNoType,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await submit_for_user_with_type.prepare(
            arguments={
                "user_id": user_id,
                "approval_type": approval_type,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": submit_for_user_with_type.workspace(workspace_id),
                "userId": user_id,
                "type": approval_type,
            },
            body=body,
        )

    def ask_submit_for_user_with_type(
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit_for_user_with_type)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_approvals_submit_for_user_with_type",
        annotations=tool_annotations("clockify_approvals_submit_for_user_with_type"),
    )
    async def clockify_approvals_submit_for_user_with_type(
        user_id: str,
        approval_type: str,
        body: CreateApprovalRequestNoType,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit_for_user_with_type)],
        approval: Annotated[
            ElicitationResult[WriteApproval], Resolve(ask_submit_for_user_with_type)
        ],
    ) -> WriteResult:
        """Submit an approval request for a user with a type."""
        return await submit_for_user_with_type.run(prepared, approval)

    resubmit = GuardedOp(
        deps,
        tool_name="clockify_approvals_resubmit",
        title="Resubmit entries for approval",
        operation_id="resubmitEntriesForApproval",
        body_model=SubmitApprovalRequestRequest,
    )

    async def prepare_resubmit(
        body: SubmitApprovalRequestRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await resubmit.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": resubmit.workspace(workspace_id)},
            body=body,
        )

    def ask_resubmit(
        prepared: Annotated[PreparedWrite, Resolve(prepare_resubmit)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_approvals_resubmit",
        annotations=tool_annotations("clockify_approvals_resubmit"),
    )
    async def clockify_approvals_resubmit(
        body: SubmitApprovalRequestRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_resubmit)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_resubmit)],
    ) -> WriteResult:
        """Resubmit rejected/withdrawn entries to an existing approval request."""
        return await resubmit.run(prepared, approval)

    resubmit_for_user = GuardedOp(
        deps,
        tool_name="clockify_approvals_resubmit_for_user",
        title="Resubmit entries for user",
        operation_id="resubmitEntriesForApprovalForUser",
        body_model=SubmitApprovalRequestRequest,
    )

    async def prepare_resubmit_for_user(
        user_id: str, body: SubmitApprovalRequestRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await resubmit_for_user.prepare(
            arguments={"user_id": user_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": resubmit_for_user.workspace(workspace_id), "userId": user_id},
            body=body,
        )

    def ask_resubmit_for_user(
        prepared: Annotated[PreparedWrite, Resolve(prepare_resubmit_for_user)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_approvals_resubmit_for_user",
        annotations=tool_annotations("clockify_approvals_resubmit_for_user"),
    )
    async def clockify_approvals_resubmit_for_user(
        user_id: str,
        body: SubmitApprovalRequestRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_resubmit_for_user)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_resubmit_for_user)],
    ) -> WriteResult:
        """Resubmit a user's rejected/withdrawn entries for approval."""
        return await resubmit_for_user.run(prepared, approval)

    update_status = GuardedOp(
        deps,
        tool_name="clockify_approvals_update_status",
        title="Update approval status",
        operation_id="updateApprovalRequest",
        body_model=UpdateApprovalRequestRequest,
    )

    async def prepare_update_status(
        approval_request_id: str,
        body: UpdateApprovalRequestRequest,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await update_status.prepare(
            arguments={
                "approval_request_id": approval_request_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update_status.workspace(workspace_id),
                "approvalRequestId": approval_request_id,
            },
            body=body,
        )

    def ask_update_status(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_approvals_update_status",
        annotations=tool_annotations("clockify_approvals_update_status"),
    )
    async def clockify_approvals_update_status(
        approval_request_id: str,
        body: UpdateApprovalRequestRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_status)],
    ) -> WriteResult:
        """Approve, reject, or withdraw an approval request."""
        return await update_status.run(prepared, approval)
