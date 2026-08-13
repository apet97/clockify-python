# pyright: reportUnusedFunction=false
"""Guarded write tools: projects."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import (
    AssignRemoveUsersRequest,
    CreateProjectFromTemplateRequest,
    CreateProjectRequest,
    RateRequest,
    UpdateProjectEstimateRequest,
    UpdateProjectMembershipsRequest,
    UpdateProjectRequest,
    UpdateProjectTemplateRequest,
)
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_projects_create",
        title="Create project",
        operation_id="createProject",
        body_model=CreateProjectRequest,
    )

    async def prepare_create(
        body: CreateProjectRequest, workspace_id: str | None = None
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
        name="clockify_projects_create", annotations=tool_annotations("clockify_projects_create")
    )
    async def clockify_projects_create(
        body: CreateProjectRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a project."""
        return await create.run(prepared, approval)

    create_from_template = GuardedOp(
        deps,
        tool_name="clockify_projects_create_from_template",
        title="Create project from template",
        operation_id="createProjectFromTemplate",
        body_model=CreateProjectFromTemplateRequest,
    )

    async def prepare_create_from_template(
        body: CreateProjectFromTemplateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await create_from_template.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": create_from_template.workspace(workspace_id)},
            body=body,
        )

    def ask_create_from_template(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create_from_template)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_projects_create_from_template",
        annotations=tool_annotations("clockify_projects_create_from_template"),
    )
    async def clockify_projects_create_from_template(
        body: CreateProjectFromTemplateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create_from_template)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create_from_template)],
    ) -> WriteResult:
        """Create a project from a template."""
        return await create_from_template.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_projects_update",
        title="Update project",
        operation_id="updateProject",
        body_model=UpdateProjectRequest,
    )

    async def prepare_update(
        project_id: str, body: UpdateProjectRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={"project_id": project_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id), "projectId": project_id},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_projects_update", annotations=tool_annotations("clockify_projects_update")
    )
    async def clockify_projects_update(
        project_id: str,
        body: UpdateProjectRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace a project (PUT: send every field you want to keep)."""
        return await update.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_projects_delete",
        title="Delete project",
        operation_id="deleteProject",
    )

    async def prepare_delete(project_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"project_id": project_id, "workspace_id": workspace_id},
            path_args={"workspaceId": delete.workspace(workspace_id), "projectId": project_id},
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_projects_delete", annotations=tool_annotations("clockify_projects_delete")
    )
    async def clockify_projects_delete(
        project_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a project. NOT reversible; archive it first."""
        return await delete.run(prepared, approval)

    set_members = GuardedOp(
        deps,
        tool_name="clockify_projects_set_members",
        title="Assign or remove project members",
        operation_id="assignOrRemoveProjectUsers",
        body_model=AssignRemoveUsersRequest,
    )

    async def prepare_set_members(
        project_id: str, body: AssignRemoveUsersRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await set_members.prepare(
            arguments={"project_id": project_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": set_members.workspace(workspace_id), "projectId": project_id},
            body=body,
        )

    def ask_set_members(
        prepared: Annotated[PreparedWrite, Resolve(prepare_set_members)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_projects_set_members",
        annotations=tool_annotations("clockify_projects_set_members"),
    )
    async def clockify_projects_set_members(
        project_id: str,
        body: AssignRemoveUsersRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_set_members)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_set_members)],
    ) -> WriteResult:
        """Assign or remove project members (changes access)."""
        return await set_members.run(prepared, approval)

    update_estimate = GuardedOp(
        deps,
        tool_name="clockify_projects_update_estimate",
        title="Update project estimate",
        operation_id="updateProjectEstimate",
        body_model=UpdateProjectEstimateRequest,
    )

    async def prepare_update_estimate(
        project_id: str, body: UpdateProjectEstimateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_estimate.prepare(
            arguments={"project_id": project_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": update_estimate.workspace(workspace_id),
                "projectId": project_id,
            },
            body=body,
        )

    def ask_update_estimate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_estimate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_projects_update_estimate",
        annotations=tool_annotations("clockify_projects_update_estimate"),
    )
    async def clockify_projects_update_estimate(
        project_id: str,
        body: UpdateProjectEstimateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_estimate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_estimate)],
    ) -> WriteResult:
        """Update a project's time/budget estimate."""
        return await update_estimate.run(prepared, approval)

    update_memberships = GuardedOp(
        deps,
        tool_name="clockify_projects_update_memberships",
        title="Update project memberships",
        operation_id="updateProjectMemberships",
        body_model=UpdateProjectMembershipsRequest,
    )

    async def prepare_update_memberships(
        project_id: str, body: UpdateProjectMembershipsRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_memberships.prepare(
            arguments={"project_id": project_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": update_memberships.workspace(workspace_id),
                "projectId": project_id,
            },
            body=body,
        )

    def ask_update_memberships(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_memberships)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_projects_update_memberships",
        annotations=tool_annotations("clockify_projects_update_memberships"),
    )
    async def clockify_projects_update_memberships(
        project_id: str,
        body: UpdateProjectMembershipsRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_memberships)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_memberships)],
    ) -> WriteResult:
        """Update project memberships (changes access)."""
        return await update_memberships.run(prepared, approval)

    update_template = GuardedOp(
        deps,
        tool_name="clockify_projects_update_template",
        title="Mark project as template",
        operation_id="updateProjectTemplate",
        body_model=UpdateProjectTemplateRequest,
    )

    async def prepare_update_template(
        project_id: str, body: UpdateProjectTemplateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_template.prepare(
            arguments={"project_id": project_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": update_template.workspace(workspace_id),
                "projectId": project_id,
            },
            body=body,
        )

    def ask_update_template(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_template)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_projects_update_template",
        annotations=tool_annotations("clockify_projects_update_template"),
    )
    async def clockify_projects_update_template(
        project_id: str,
        body: UpdateProjectTemplateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_template)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_template)],
    ) -> WriteResult:
        """Set or clear the project's template flag."""
        return await update_template.run(prepared, approval)

    update_user_cost_rate = GuardedOp(
        deps,
        tool_name="clockify_projects_update_user_cost_rate",
        title="Update project member cost rate",
        operation_id="updateProjectUserCostRate",
        body_model=RateRequest,
    )

    async def prepare_update_user_cost_rate(
        project_id: str, user_id: str, body: RateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_user_cost_rate.prepare(
            arguments={
                "project_id": project_id,
                "user_id": user_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update_user_cost_rate.workspace(workspace_id),
                "projectId": project_id,
                "userId": user_id,
            },
            body=body,
        )

    def ask_update_user_cost_rate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_user_cost_rate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_projects_update_user_cost_rate",
        annotations=tool_annotations("clockify_projects_update_user_cost_rate"),
    )
    async def clockify_projects_update_user_cost_rate(
        project_id: str,
        user_id: str,
        body: RateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_user_cost_rate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_user_cost_rate)],
    ) -> WriteResult:
        """Set a member's cost rate on this project."""
        return await update_user_cost_rate.run(prepared, approval)

    update_user_hourly_rate = GuardedOp(
        deps,
        tool_name="clockify_projects_update_user_hourly_rate",
        title="Update project member billable rate",
        operation_id="updateProjectUserHourlyRate",
        body_model=RateRequest,
    )

    async def prepare_update_user_hourly_rate(
        project_id: str, user_id: str, body: RateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_user_hourly_rate.prepare(
            arguments={
                "project_id": project_id,
                "user_id": user_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update_user_hourly_rate.workspace(workspace_id),
                "projectId": project_id,
                "userId": user_id,
            },
            body=body,
        )

    def ask_update_user_hourly_rate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_user_hourly_rate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_projects_update_user_hourly_rate",
        annotations=tool_annotations("clockify_projects_update_user_hourly_rate"),
    )
    async def clockify_projects_update_user_hourly_rate(
        project_id: str,
        user_id: str,
        body: RateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_user_hourly_rate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_user_hourly_rate)],
    ) -> WriteResult:
        """Set a member's billable rate on this project."""
        return await update_user_hourly_rate.run(prepared, approval)
