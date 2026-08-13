# pyright: reportUnusedFunction=false
"""Guarded write tools: time off requests."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import ChangeTimeOffRequestStatusRequest, CreateTimeOffRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    submit = GuardedOp(
        deps,
        tool_name="clockify_time_off_requests_submit",
        title="Submit time-off request",
        operation_id="createTimeOffRequest",
        body_model=CreateTimeOffRequest,
    )

    async def prepare_submit(
        policy_id: str, body: CreateTimeOffRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await submit.prepare(
            arguments={"policy_id": policy_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": submit.workspace(workspace_id), "policyId": policy_id},
            body=body,
        )

    def ask_submit(
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_requests_submit",
        annotations=tool_annotations("clockify_time_off_requests_submit"),
    )
    async def clockify_time_off_requests_submit(
        policy_id: str,
        body: CreateTimeOffRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_submit)],
    ) -> WriteResult:
        """Submit a time-off request under a policy."""
        return await submit.run(prepared, approval)

    submit_for_user = GuardedOp(
        deps,
        tool_name="clockify_time_off_requests_submit_for_user",
        title="Submit time-off for user",
        operation_id="createTimeOffRequestForUser",
        body_model=CreateTimeOffRequest,
    )

    async def prepare_submit_for_user(
        policy_id: str, user_id: str, body: CreateTimeOffRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await submit_for_user.prepare(
            arguments={
                "policy_id": policy_id,
                "user_id": user_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": submit_for_user.workspace(workspace_id),
                "policyId": policy_id,
                "userId": user_id,
            },
            body=body,
        )

    def ask_submit_for_user(
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit_for_user)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_requests_submit_for_user",
        annotations=tool_annotations("clockify_time_off_requests_submit_for_user"),
    )
    async def clockify_time_off_requests_submit_for_user(
        policy_id: str,
        user_id: str,
        body: CreateTimeOffRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_submit_for_user)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_submit_for_user)],
    ) -> WriteResult:
        """Submit a time-off request for another user."""
        return await submit_for_user.run(prepared, approval)

    update_status = GuardedOp(
        deps,
        tool_name="clockify_time_off_requests_update_status",
        title="Change time-off request status",
        operation_id="changeTimeOffRequestStatus",
        body_model=ChangeTimeOffRequestStatusRequest,
    )

    async def prepare_update_status(
        policy_id: str,
        request_id: str,
        body: ChangeTimeOffRequestStatusRequest,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await update_status.prepare(
            arguments={
                "policy_id": policy_id,
                "request_id": request_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update_status.workspace(workspace_id),
                "policyId": policy_id,
                "requestId": request_id,
            },
            body=body,
        )

    def ask_update_status(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_requests_update_status",
        annotations=tool_annotations("clockify_time_off_requests_update_status"),
    )
    async def clockify_time_off_requests_update_status(
        policy_id: str,
        request_id: str,
        body: ChangeTimeOffRequestStatusRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_status)],
    ) -> WriteResult:
        """Approve or reject a time-off request."""
        return await update_status.run(prepared, approval)

    withdraw = GuardedOp(
        deps,
        tool_name="clockify_time_off_requests_withdraw",
        title="Withdraw time-off request",
        operation_id="deleteTimeOffRequest",
    )

    async def prepare_withdraw(
        policy_id: str, request_id: str, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await withdraw.prepare(
            arguments={
                "policy_id": policy_id,
                "request_id": request_id,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": withdraw.workspace(workspace_id),
                "policyId": policy_id,
                "requestId": request_id,
            },
        )

    def ask_withdraw(
        prepared: Annotated[PreparedWrite, Resolve(prepare_withdraw)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_off_requests_withdraw",
        annotations=tool_annotations("clockify_time_off_requests_withdraw"),
    )
    async def clockify_time_off_requests_withdraw(
        policy_id: str,
        request_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_withdraw)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_withdraw)],
    ) -> WriteResult:
        """Withdraw (delete) a PENDING time-off request. NOT reversible."""
        return await withdraw.run(prepared, approval)
