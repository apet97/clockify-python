# pyright: reportUnusedFunction=false
"""Guarded write tools: tasks."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import RateUpdateRequest, TaskCreateRequest, TaskUpdateRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_tasks_create",
        title="Create task",
        operation_id="addTaskOnProject",
        body_model=TaskCreateRequest,
    )

    async def prepare_create(
        project_id: str,
        body: TaskCreateRequest,
        contains_assignee: bool | str | None = None,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await create.prepare(
            arguments={
                "project_id": project_id,
                "body": body,
                "contains_assignee": contains_assignee,
                "workspace_id": workspace_id,
            },
            path_args={"workspaceId": create.workspace(workspace_id), "projectId": project_id},
            body=body,
            query={"contains_assignee": contains_assignee},
        )

    def ask_create(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_tasks_create", annotations=tool_annotations("clockify_tasks_create")
    )
    async def clockify_tasks_create(
        project_id: str,
        body: TaskCreateRequest,
        contains_assignee: bool | str | None = None,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a task on a project."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_tasks_update",
        title="Update task",
        operation_id="updateTaskOnProject",
        body_model=TaskUpdateRequest,
    )

    async def prepare_update(
        project_id: str,
        task_id: str,
        body: TaskUpdateRequest,
        contains_assignee: bool | str | None = None,
        membership_status: bool | str | None = None,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={
                "project_id": project_id,
                "task_id": task_id,
                "body": body,
                "contains_assignee": contains_assignee,
                "membership_status": membership_status,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update.workspace(workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
            body=body,
            query={"contains_assignee": contains_assignee, "membership_status": membership_status},
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_tasks_update", annotations=tool_annotations("clockify_tasks_update")
    )
    async def clockify_tasks_update(
        project_id: str,
        task_id: str,
        body: TaskUpdateRequest,
        contains_assignee: bool | str | None = None,
        membership_status: bool | str | None = None,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace a task (PUT: send every field you want to keep)."""
        return await update.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_tasks_delete",
        title="Delete task",
        operation_id="deleteTaskFromProject",
    )

    async def prepare_delete(
        project_id: str, task_id: str, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await delete.prepare(
            arguments={"project_id": project_id, "task_id": task_id, "workspace_id": workspace_id},
            path_args={
                "workspaceId": delete.workspace(workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_tasks_delete", annotations=tool_annotations("clockify_tasks_delete")
    )
    async def clockify_tasks_delete(
        project_id: str,
        task_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a task. NOT reversible; mark it DONE first."""
        return await delete.run(prepared, approval)

    update_billable_rate = GuardedOp(
        deps,
        tool_name="clockify_tasks_update_billable_rate",
        title="Update task billable rate",
        operation_id="updateTaskBillableRate",
        body_model=RateUpdateRequest,
    )

    async def prepare_update_billable_rate(
        project_id: str, task_id: str, body: RateUpdateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_billable_rate.prepare(
            arguments={
                "project_id": project_id,
                "task_id": task_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update_billable_rate.workspace(workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
            body=body,
        )

    def ask_update_billable_rate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_billable_rate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_tasks_update_billable_rate",
        annotations=tool_annotations("clockify_tasks_update_billable_rate"),
    )
    async def clockify_tasks_update_billable_rate(
        project_id: str,
        task_id: str,
        body: RateUpdateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_billable_rate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_billable_rate)],
    ) -> WriteResult:
        """Set the task's billable rate."""
        return await update_billable_rate.run(prepared, approval)

    update_cost_rate = GuardedOp(
        deps,
        tool_name="clockify_tasks_update_cost_rate",
        title="Update task cost rate",
        operation_id="updateTaskCostRate",
        body_model=RateUpdateRequest,
    )

    async def prepare_update_cost_rate(
        project_id: str, task_id: str, body: RateUpdateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_cost_rate.prepare(
            arguments={
                "project_id": project_id,
                "task_id": task_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update_cost_rate.workspace(workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
            body=body,
        )

    def ask_update_cost_rate(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_cost_rate)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_tasks_update_cost_rate",
        annotations=tool_annotations("clockify_tasks_update_cost_rate"),
    )
    async def clockify_tasks_update_cost_rate(
        project_id: str,
        task_id: str,
        body: RateUpdateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_cost_rate)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_cost_rate)],
    ) -> WriteResult:
        """Set the task's cost rate."""
        return await update_cost_rate.run(prepared, approval)
