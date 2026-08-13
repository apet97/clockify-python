# pyright: reportUnusedFunction=false
"""Guarded write tools: custom fields."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import (
    CreateCustomFieldRequest,
    UpdateCustomFieldRequest,
    UpdateProjectCustomFieldRequest,
)
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create_for_workspace = GuardedOp(
        deps,
        tool_name="clockify_custom_fields_create_for_workspace",
        title="Create custom field",
        operation_id="createWorkspaceCustomField",
        body_model=CreateCustomFieldRequest,
    )

    async def prepare_create_for_workspace(
        body: CreateCustomFieldRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await create_for_workspace.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": create_for_workspace.workspace(workspace_id)},
            body=body,
        )

    def ask_create_for_workspace(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create_for_workspace)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_custom_fields_create_for_workspace",
        annotations=tool_annotations("clockify_custom_fields_create_for_workspace"),
    )
    async def clockify_custom_fields_create_for_workspace(
        body: CreateCustomFieldRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create_for_workspace)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create_for_workspace)],
    ) -> WriteResult:
        """Create a workspace custom field."""
        return await create_for_workspace.run(prepared, approval)

    update_for_workspace = GuardedOp(
        deps,
        tool_name="clockify_custom_fields_update_for_workspace",
        title="Update custom field",
        operation_id="updateWorkspaceCustomField",
        body_model=UpdateCustomFieldRequest,
    )

    async def prepare_update_for_workspace(
        custom_field_id: str, body: UpdateCustomFieldRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_for_workspace.prepare(
            arguments={
                "custom_field_id": custom_field_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update_for_workspace.workspace(workspace_id),
                "customFieldId": custom_field_id,
            },
            body=body,
        )

    def ask_update_for_workspace(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_for_workspace)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_custom_fields_update_for_workspace",
        annotations=tool_annotations("clockify_custom_fields_update_for_workspace"),
    )
    async def clockify_custom_fields_update_for_workspace(
        custom_field_id: str,
        body: UpdateCustomFieldRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_for_workspace)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_for_workspace)],
    ) -> WriteResult:
        """Replace a workspace custom field (PUT)."""
        return await update_for_workspace.run(prepared, approval)

    delete_for_workspace = GuardedOp(
        deps,
        tool_name="clockify_custom_fields_delete_for_workspace",
        title="Delete custom field",
        operation_id="deleteWorkspaceCustomField",
    )

    async def prepare_delete_for_workspace(
        custom_field_id: str, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await delete_for_workspace.prepare(
            arguments={"custom_field_id": custom_field_id, "workspace_id": workspace_id},
            path_args={
                "workspaceId": delete_for_workspace.workspace(workspace_id),
                "customFieldId": custom_field_id,
            },
        )

    def ask_delete_for_workspace(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete_for_workspace)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_custom_fields_delete_for_workspace",
        annotations=tool_annotations("clockify_custom_fields_delete_for_workspace"),
    )
    async def clockify_custom_fields_delete_for_workspace(
        custom_field_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete_for_workspace)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete_for_workspace)],
    ) -> WriteResult:
        """Delete a workspace custom field. NOT reversible."""
        return await delete_for_workspace.run(prepared, approval)

    update_for_project = GuardedOp(
        deps,
        tool_name="clockify_custom_fields_update_for_project",
        title="Update project custom field",
        operation_id="updateProjectCustomField",
        body_model=UpdateProjectCustomFieldRequest,
    )

    async def prepare_update_for_project(
        project_id: str,
        custom_field_id: str,
        body: UpdateProjectCustomFieldRequest,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await update_for_project.prepare(
            arguments={
                "project_id": project_id,
                "custom_field_id": custom_field_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update_for_project.workspace(workspace_id),
                "projectId": project_id,
                "customFieldId": custom_field_id,
            },
            body=body,
        )

    def ask_update_for_project(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_for_project)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_custom_fields_update_for_project",
        annotations=tool_annotations("clockify_custom_fields_update_for_project"),
    )
    async def clockify_custom_fields_update_for_project(
        project_id: str,
        custom_field_id: str,
        body: UpdateProjectCustomFieldRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_for_project)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_for_project)],
    ) -> WriteResult:
        """Update a custom field's project-level default."""
        return await update_for_project.run(prepared, approval)

    remove_from_project = GuardedOp(
        deps,
        tool_name="clockify_custom_fields_remove_from_project",
        title="Remove project custom field",
        operation_id="removeProjectCustomField",
    )

    async def prepare_remove_from_project(
        project_id: str, custom_field_id: str, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await remove_from_project.prepare(
            arguments={
                "project_id": project_id,
                "custom_field_id": custom_field_id,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": remove_from_project.workspace(workspace_id),
                "projectId": project_id,
                "customFieldId": custom_field_id,
            },
        )

    def ask_remove_from_project(
        prepared: Annotated[PreparedWrite, Resolve(prepare_remove_from_project)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_custom_fields_remove_from_project",
        annotations=tool_annotations("clockify_custom_fields_remove_from_project"),
    )
    async def clockify_custom_fields_remove_from_project(
        project_id: str,
        custom_field_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_remove_from_project)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_remove_from_project)],
    ) -> WriteResult:
        """Remove a custom field from a project. NOT reversible."""
        return await remove_from_project.run(prepared, approval)
