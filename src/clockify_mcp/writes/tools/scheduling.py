# pyright: reportUnusedFunction=false
"""Guarded write tools: scheduling."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import (
    ChangeRecurringPeriodRequest,
    CopyAssignmentRequest,
    CreateRecurringAssignmentRequest,
    PublishAssignmentsRequest,
    UpdateRecurringAssignmentRequest,
)
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create_recurring = GuardedOp(
        deps,
        tool_name="clockify_scheduling_create_recurring",
        title="Create scheduled assignment",
        operation_id="createRecurringAssignment",
        body_model=CreateRecurringAssignmentRequest,
    )

    async def prepare_create_recurring(
        body: CreateRecurringAssignmentRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await create_recurring.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": create_recurring.workspace(workspace_id)},
            body=body,
        )

    def ask_create_recurring(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create_recurring)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_scheduling_create_recurring",
        annotations=tool_annotations("clockify_scheduling_create_recurring"),
    )
    async def clockify_scheduling_create_recurring(
        body: CreateRecurringAssignmentRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create_recurring)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create_recurring)],
    ) -> WriteResult:
        """Create a (possibly recurring) scheduled assignment."""
        return await create_recurring.run(prepared, approval)

    update_recurring = GuardedOp(
        deps,
        tool_name="clockify_scheduling_update_recurring",
        title="Update scheduled assignment",
        operation_id="updateRecurringAssignment",
        body_model=UpdateRecurringAssignmentRequest,
    )

    async def prepare_update_recurring(
        assignment_id: str, body: UpdateRecurringAssignmentRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_recurring.prepare(
            arguments={"assignment_id": assignment_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": update_recurring.workspace(workspace_id),
                "assignmentId": assignment_id,
            },
            body=body,
        )

    def ask_update_recurring(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_recurring)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_scheduling_update_recurring",
        annotations=tool_annotations("clockify_scheduling_update_recurring"),
    )
    async def clockify_scheduling_update_recurring(
        assignment_id: str,
        body: UpdateRecurringAssignmentRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_recurring)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_recurring)],
    ) -> WriteResult:
        """Update a scheduled assignment."""
        return await update_recurring.run(prepared, approval)

    delete_recurring = GuardedOp(
        deps,
        tool_name="clockify_scheduling_delete_recurring",
        title="Delete scheduled assignment",
        operation_id="deleteRecurringAssignment",
    )

    async def prepare_delete_recurring(
        assignment_id: str,
        series_update_option: bool | str | None = None,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await delete_recurring.prepare(
            arguments={
                "assignment_id": assignment_id,
                "series_update_option": series_update_option,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": delete_recurring.workspace(workspace_id),
                "assignmentId": assignment_id,
            },
            query={"series_update_option": series_update_option},
        )

    def ask_delete_recurring(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete_recurring)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_scheduling_delete_recurring",
        annotations=tool_annotations("clockify_scheduling_delete_recurring"),
    )
    async def clockify_scheduling_delete_recurring(
        assignment_id: str,
        series_update_option: bool | str | None = None,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete_recurring)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete_recurring)],
    ) -> WriteResult:
        """Delete a scheduled assignment. NOT reversible."""
        return await delete_recurring.run(prepared, approval)

    change_recurring_period = GuardedOp(
        deps,
        tool_name="clockify_scheduling_change_recurring_period",
        title="Change recurring period",
        operation_id="changeRecurringPeriod",
        body_model=ChangeRecurringPeriodRequest,
    )

    async def prepare_change_recurring_period(
        assignment_id: str, body: ChangeRecurringPeriodRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await change_recurring_period.prepare(
            arguments={"assignment_id": assignment_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": change_recurring_period.workspace(workspace_id),
                "assignmentId": assignment_id,
            },
            body=body,
        )

    def ask_change_recurring_period(
        prepared: Annotated[PreparedWrite, Resolve(prepare_change_recurring_period)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_scheduling_change_recurring_period",
        annotations=tool_annotations("clockify_scheduling_change_recurring_period"),
    )
    async def clockify_scheduling_change_recurring_period(
        assignment_id: str,
        body: ChangeRecurringPeriodRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_change_recurring_period)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_change_recurring_period)],
    ) -> WriteResult:
        """Change the recurring period of an assignment series (PUT)."""
        return await change_recurring_period.run(prepared, approval)

    copy_assignment = GuardedOp(
        deps,
        tool_name="clockify_scheduling_copy_assignment",
        title="Copy scheduled assignment",
        operation_id="copyScheduledAssignment",
        body_model=CopyAssignmentRequest,
    )

    async def prepare_copy_assignment(
        assignment_id: str, body: CopyAssignmentRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await copy_assignment.prepare(
            arguments={"assignment_id": assignment_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": copy_assignment.workspace(workspace_id),
                "assignmentId": assignment_id,
            },
            body=body,
        )

    def ask_copy_assignment(
        prepared: Annotated[PreparedWrite, Resolve(prepare_copy_assignment)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_scheduling_copy_assignment",
        annotations=tool_annotations("clockify_scheduling_copy_assignment"),
    )
    async def clockify_scheduling_copy_assignment(
        assignment_id: str,
        body: CopyAssignmentRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_copy_assignment)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_copy_assignment)],
    ) -> WriteResult:
        """Copy a scheduled assignment."""
        return await copy_assignment.run(prepared, approval)

    publish_assignments = GuardedOp(
        deps,
        tool_name="clockify_scheduling_publish_assignments",
        title="Publish assignments",
        operation_id="publishAssignments",
        body_model=PublishAssignmentsRequest,
    )

    async def prepare_publish_assignments(
        body: PublishAssignmentsRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await publish_assignments.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": publish_assignments.workspace(workspace_id)},
            body=body,
        )

    def ask_publish_assignments(
        prepared: Annotated[PreparedWrite, Resolve(prepare_publish_assignments)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_scheduling_publish_assignments",
        annotations=tool_annotations("clockify_scheduling_publish_assignments"),
    )
    async def clockify_scheduling_publish_assignments(
        body: PublishAssignmentsRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_publish_assignments)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_publish_assignments)],
    ) -> WriteResult:
        """Publish scheduled assignments (bulk)."""
        return await publish_assignments.run(prepared, approval)
