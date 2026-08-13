# pyright: reportUnusedFunction=false
"""Guarded write tools: holidays."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import CreateHolidayRequest, UpdateHolidayRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_holidays_create",
        title="Create holiday",
        operation_id="createHoliday",
        body_model=CreateHolidayRequest,
    )

    async def prepare_create(
        body: CreateHolidayRequest, workspace_id: str | None = None
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
        name="clockify_holidays_create", annotations=tool_annotations("clockify_holidays_create")
    )
    async def clockify_holidays_create(
        body: CreateHolidayRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a holiday."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_holidays_update",
        title="Update holiday",
        operation_id="updateHoliday",
        body_model=UpdateHolidayRequest,
    )

    async def prepare_update(
        holiday_id: str, body: UpdateHolidayRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={"holiday_id": holiday_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id), "holidayId": holiday_id},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_holidays_update", annotations=tool_annotations("clockify_holidays_update")
    )
    async def clockify_holidays_update(
        holiday_id: str,
        body: UpdateHolidayRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace a holiday (PUT)."""
        return await update.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_holidays_delete",
        title="Delete holiday",
        operation_id="deleteHoliday",
    )

    async def prepare_delete(holiday_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"holiday_id": holiday_id, "workspace_id": workspace_id},
            path_args={"workspaceId": delete.workspace(workspace_id), "holidayId": holiday_id},
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_holidays_delete", annotations=tool_annotations("clockify_holidays_delete")
    )
    async def clockify_holidays_delete(
        holiday_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a holiday. NOT reversible."""
        return await delete.run(prepared, approval)
