# pyright: reportUnusedFunction=false
"""Guarded write tools: user groups."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import AddUserToGroupRequest, UserGroupRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_user_groups_create",
        title="Create user group",
        operation_id="addNewGroup",
        body_model=UserGroupRequest,
    )

    async def prepare_create(
        body: UserGroupRequest, workspace_id: str | None = None
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
        name="clockify_user_groups_create",
        annotations=tool_annotations("clockify_user_groups_create"),
    )
    async def clockify_user_groups_create(
        body: UserGroupRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a user group."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_user_groups_update",
        title="Update user group",
        operation_id="updateGroup",
        body_model=UserGroupRequest,
    )

    async def prepare_update(
        group_id: str, body: UserGroupRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={"group_id": group_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id), "groupId": group_id},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_user_groups_update",
        annotations=tool_annotations("clockify_user_groups_update"),
    )
    async def clockify_user_groups_update(
        group_id: str,
        body: UserGroupRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace a user group (PUT)."""
        return await update.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_user_groups_delete",
        title="Delete user group",
        operation_id="deleteGroup",
    )

    async def prepare_delete(group_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"group_id": group_id, "workspace_id": workspace_id},
            path_args={"workspaceId": delete.workspace(workspace_id), "groupId": group_id},
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_user_groups_delete",
        annotations=tool_annotations("clockify_user_groups_delete"),
    )
    async def clockify_user_groups_delete(
        group_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a user group. NOT reversible."""
        return await delete.run(prepared, approval)

    add_members = GuardedOp(
        deps,
        tool_name="clockify_user_groups_add_members",
        title="Add group members",
        operation_id="addUsersToGroup",
        body_model=AddUserToGroupRequest,
    )

    async def prepare_add_members(
        group_id: str, body: AddUserToGroupRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await add_members.prepare(
            arguments={"group_id": group_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": add_members.workspace(workspace_id), "groupId": group_id},
            body=body,
        )

    def ask_add_members(
        prepared: Annotated[PreparedWrite, Resolve(prepare_add_members)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_user_groups_add_members",
        annotations=tool_annotations("clockify_user_groups_add_members"),
    )
    async def clockify_user_groups_add_members(
        group_id: str,
        body: AddUserToGroupRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_add_members)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_add_members)],
    ) -> WriteResult:
        """Add users to a group (changes access)."""
        return await add_members.run(prepared, approval)

    remove_member = GuardedOp(
        deps,
        tool_name="clockify_user_groups_remove_member",
        title="Remove group member",
        operation_id="removeUserFromGroup",
    )

    async def prepare_remove_member(
        group_id: str, user_id: str, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await remove_member.prepare(
            arguments={"group_id": group_id, "user_id": user_id, "workspace_id": workspace_id},
            path_args={
                "workspaceId": remove_member.workspace(workspace_id),
                "groupId": group_id,
                "userId": user_id,
            },
        )

    def ask_remove_member(
        prepared: Annotated[PreparedWrite, Resolve(prepare_remove_member)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_user_groups_remove_member",
        annotations=tool_annotations("clockify_user_groups_remove_member"),
    )
    async def clockify_user_groups_remove_member(
        group_id: str,
        user_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_remove_member)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_remove_member)],
    ) -> WriteResult:
        """Remove a user from a group (changes access)."""
        return await remove_member.run(prepared, approval)
