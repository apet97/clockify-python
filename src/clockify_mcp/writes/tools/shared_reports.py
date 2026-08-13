# pyright: reportUnusedFunction=false
"""Guarded write tools: shared reports."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import SharedReportCreate
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_shared_reports_create",
        title="Create shared report",
        operation_id="postWorkspacesWorkspaceIdSharedReports",
        body_model=SharedReportCreate,
    )

    async def prepare_create(
        body: SharedReportCreate, workspace_id: str | None = None
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
        name="clockify_shared_reports_create",
        annotations=tool_annotations("clockify_shared_reports_create"),
    )
    async def clockify_shared_reports_create(
        body: SharedReportCreate,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a shared report (publishes report access)."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_shared_reports_update",
        title="Update shared report",
        operation_id="putWorkspacesWorkspaceIdSharedReportsSharedReportId",
        body_model=SharedReportCreate,
    )

    async def prepare_update(
        shared_report_id: str, body: SharedReportCreate, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={
                "shared_report_id": shared_report_id,
                "body": body,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": update.workspace(workspace_id),
                "sharedReportId": shared_report_id,
            },
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_shared_reports_update",
        annotations=tool_annotations("clockify_shared_reports_update"),
    )
    async def clockify_shared_reports_update(
        shared_report_id: str,
        body: SharedReportCreate,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Update a shared report."""
        return await update.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_shared_reports_delete",
        title="Delete shared report",
        operation_id="deleteWorkspacesWorkspaceIdSharedReportsSharedReportId",
    )

    async def prepare_delete(
        shared_report_id: str, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await delete.prepare(
            arguments={"shared_report_id": shared_report_id, "workspace_id": workspace_id},
            path_args={
                "workspaceId": delete.workspace(workspace_id),
                "sharedReportId": shared_report_id,
            },
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_shared_reports_delete",
        annotations=tool_annotations("clockify_shared_reports_delete"),
    )
    async def clockify_shared_reports_delete(
        shared_report_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a shared report. NOT reversible."""
        return await delete.run(prepared, approval)
