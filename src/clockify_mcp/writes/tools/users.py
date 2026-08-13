# pyright: reportUnusedFunction=false
"""Guarded write tools: users."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import (
    AddLimitedUsersRequest,
    AddUserToWorkspaceRequest,
    ManagerRoleRequest,
    UpdateCostRateRequest,
    UpdateUserCustomFieldValueRequest,
    UpdateUserHourlyRateRequest,
    UpdateUserStatusRequest,
)
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    add_to_workspace = GuardedOp(
        deps,
        tool_name="clockify_users_add_to_workspace",
        title="Invite user to workspace",
        operation_id="addUserToWorkspace",
        body_model=AddUserToWorkspaceRequest,
    )

    async def prepare_add_to_workspace(
        body: AddUserToWorkspaceRequest,
        send_email: bool | str | None = None,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await add_to_workspace.prepare(
            arguments={"body": body, "send_email": send_email, "workspace_id": workspace_id},
            path_args={"workspaceId": add_to_workspace.workspace(workspace_id)},
            body=body,
            query={"send_email": send_email},
        )

    def ask_add_to_workspace(
        prepared: Annotated[PreparedWrite, Resolve(prepare_add_to_workspace)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_users_add_to_workspace",
        annotations=tool_annotations("clockify_users_add_to_workspace"),
    )
    async def clockify_users_add_to_workspace(
        body: AddUserToWorkspaceRequest,
        send_email: bool | str | None = None,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_add_to_workspace)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_add_to_workspace)],
    ) -> WriteResult:
        """Invite a user to the workspace (changes access)."""
        return await add_to_workspace.run(prepared, approval)

    add_limited_to_workspace = GuardedOp(
        deps,
        tool_name="clockify_users_add_limited_to_workspace",
        title="Add limited users",
        operation_id="addLimitedUsersWithInfo",
        body_model=AddLimitedUsersRequest,
    )

    async def prepare_add_limited_to_workspace(
        body: AddLimitedUsersRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await add_limited_to_workspace.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": add_limited_to_workspace.workspace(workspace_id)},
            body=body,
        )

    def ask_add_limited_to_workspace(
        prepared: Annotated[PreparedWrite, Resolve(prepare_add_limited_to_workspace)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_users_add_limited_to_workspace",
        annotations=tool_annotations("clockify_users_add_limited_to_workspace"),
    )
    async def clockify_users_add_limited_to_workspace(
        body: AddLimitedUsersRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_add_limited_to_workspace)],
        approval: Annotated[
            ElicitationResult[WriteApproval], Resolve(ask_add_limited_to_workspace)
        ],
    ) -> WriteResult:
        """Add limited (seat-only) users to the workspace (changes access)."""
        return await add_limited_to_workspace.run(prepared, approval)

    grant_manager_role = GuardedOp(
        deps,
        tool_name="clockify_users_grant_manager_role",
        title="Grant manager role",
        operation_id="giveUserManagerRole",
        body_model=ManagerRoleRequest,
    )

    async def prepare_grant_manager_role(
        user_id: str, body: ManagerRoleRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await grant_manager_role.prepare(
            arguments={"user_id": user_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": grant_manager_role.workspace(workspace_id),
                "userId": user_id,
            },
            body=body,
        )

    def ask_grant_manager_role(
        prepared: Annotated[PreparedWrite, Resolve(prepare_grant_manager_role)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_users_grant_manager_role",
        annotations=tool_annotations("clockify_users_grant_manager_role"),
    )
    async def clockify_users_grant_manager_role(
        user_id: str,
        body: ManagerRoleRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_grant_manager_role)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_grant_manager_role)],
    ) -> WriteResult:
        """Grant a manager role to a user (changes access)."""
        return await grant_manager_role.run(prepared, approval)

    revoke_manager_role = GuardedOp(
        deps,
        tool_name="clockify_users_revoke_manager_role",
        title="Revoke manager role",
        operation_id="removeUserManagerRole",
        body_model=ManagerRoleRequest,
    )

    async def prepare_revoke_manager_role(
        user_id: str, body: ManagerRoleRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await revoke_manager_role.prepare(
            arguments={"user_id": user_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": revoke_manager_role.workspace(workspace_id),
                "userId": user_id,
            },
            body=body,
        )

    def ask_revoke_manager_role(
        prepared: Annotated[PreparedWrite, Resolve(prepare_revoke_manager_role)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_users_revoke_manager_role",
        annotations=tool_annotations("clockify_users_revoke_manager_role"),
    )
    async def clockify_users_revoke_manager_role(
        user_id: str,
        body: ManagerRoleRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_revoke_manager_role)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_revoke_manager_role)],
    ) -> WriteResult:
        """Revoke a manager role from a user (changes access)."""
        return await revoke_manager_role.run(prepared, approval)

    update_cost_rate = GuardedOp(
        deps,
        tool_name="clockify_users_update_cost_rate",
        title="Update user cost rate",
        operation_id="updateUserCostRate",
        body_model=UpdateCostRateRequest,
    )

    async def prepare_update_cost_rate(
        user_id: str, body: UpdateCostRateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_cost_rate.prepare(
            arguments={"user_id": user_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update_cost_rate.workspace(workspace_id), "userId": user_id},
            body=body,
        )

    def ask_update_cost_rate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_cost_rate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_users_update_cost_rate",
        annotations=tool_annotations("clockify_users_update_cost_rate"),
    )
    async def clockify_users_update_cost_rate(
        user_id: str,
        body: UpdateCostRateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_cost_rate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_cost_rate)],
    ) -> WriteResult:
        """Set a user's workspace cost rate."""
        return await update_cost_rate.run(prepared, approval)

    update_hourly_rate = GuardedOp(
        deps,
        tool_name="clockify_users_update_hourly_rate",
        title="Update user billable rate",
        operation_id="updateUserHourlyRate",
        body_model=UpdateUserHourlyRateRequest,
    )

    async def prepare_update_hourly_rate(
        user_id: str, body: UpdateUserHourlyRateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_hourly_rate.prepare(
            arguments={"user_id": user_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": update_hourly_rate.workspace(workspace_id),
                "userId": user_id,
            },
            body=body,
        )

    def ask_update_hourly_rate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_hourly_rate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_users_update_hourly_rate",
        annotations=tool_annotations("clockify_users_update_hourly_rate"),
    )
    async def clockify_users_update_hourly_rate(
        user_id: str,
        body: UpdateUserHourlyRateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_hourly_rate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_hourly_rate)],
    ) -> WriteResult:
        """Set a user's workspace billable rate."""
        return await update_hourly_rate.run(prepared, approval)

    update_status = GuardedOp(
        deps,
        tool_name="clockify_users_update_status",
        title="Update user status",
        operation_id="updateUserStatus",
        body_model=UpdateUserStatusRequest,
    )

    async def prepare_update_status(
        user_id: str, body: UpdateUserStatusRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_status.prepare(
            arguments={"user_id": user_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update_status.workspace(workspace_id), "userId": user_id},
            body=body,
        )

    def ask_update_status(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_users_update_status",
        annotations=tool_annotations("clockify_users_update_status"),
    )
    async def clockify_users_update_status(
        user_id: str,
        body: UpdateUserStatusRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_status)],
    ) -> WriteResult:
        """Activate or deactivate a workspace member (changes access)."""
        return await update_status.run(prepared, approval)

    update_custom_field_value = GuardedOp(
        deps,
        tool_name="clockify_users_update_custom_field_value",
        title="Update user custom field",
        operation_id="updateUserCustomFieldValue",
        body_model=UpdateUserCustomFieldValueRequest,
    )

    async def prepare_update_custom_field_value(
        user_id: str,
        custom_field_id: str,
        body: UpdateUserCustomFieldValueRequest,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await update_custom_field_value.prepare(
            arguments={
                "user_id": user_id,
                "custom_field_id": custom_field_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update_custom_field_value.workspace(workspace_id),
                "userId": user_id,
                "customFieldId": custom_field_id,
            },
            body=body,
        )

    def ask_update_custom_field_value(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_custom_field_value)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_users_update_custom_field_value",
        annotations=tool_annotations("clockify_users_update_custom_field_value"),
    )
    async def clockify_users_update_custom_field_value(
        user_id: str,
        custom_field_id: str,
        body: UpdateUserCustomFieldValueRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_custom_field_value)],
        approval: Annotated[
            ElicitationResult[WriteApproval], Resolve(ask_update_custom_field_value)
        ],
    ) -> WriteResult:
        """Set a user's custom-field value (PUT)."""
        return await update_custom_field_value.run(prepared, approval)
