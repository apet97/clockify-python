# pyright: reportUnusedFunction=false
"""Write tools: time entries.

Personal time tracking is the routine tier: create, update, duplicate, and
stop execute directly without an approval round trip. Everything that touches
other users in bulk, marks entries invoiced, or deletes is guarded.
"""

from typing import Annotated, Any

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import CreateTimeEntryRequest, TimeEntryCreate, TimeEntryUpdate
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.plans import enforce_bulk_caps
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, RoutineOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:
    create = RoutineOp(
        deps,
        tool_name="clockify_time_entries_create",
        title="Create time entry",
        operation_id="postWorkspacesWorkspaceIdTimeEntries",
        body_model=CreateTimeEntryRequest,
    )

    @server.tool(
        name="clockify_time_entries_create",
        annotations=tool_annotations("clockify_time_entries_create"),
    )
    async def clockify_time_entries_create(
        body: CreateTimeEntryRequest,
        workspace_id: str | None = None,
    ) -> WriteResult:
        """Create a time entry (omit `end` to start a running timer)."""
        return await create.execute(
            path_args={"workspaceId": create.workspace(workspace_id)}, body=body
        )

    create_for_user = RoutineOp(
        deps,
        tool_name="clockify_time_entries_create_for_user",
        title="Create time entry for user",
        operation_id="postWorkspacesWorkspaceIdUserUserIdTimeEntries",
        body_model=TimeEntryCreate,
    )

    @server.tool(
        name="clockify_time_entries_create_for_user",
        annotations=tool_annotations("clockify_time_entries_create_for_user"),
    )
    async def clockify_time_entries_create_for_user(
        user_id: str,
        body: TimeEntryCreate,
        workspace_id: str | None = None,
    ) -> WriteResult:
        """Create a time entry for another user (requires admin/manager rights)."""
        return await create_for_user.execute(
            path_args={
                "workspaceId": create_for_user.workspace(workspace_id),
                "userId": user_id,
            },
            body=body,
        )

    update = RoutineOp(
        deps,
        tool_name="clockify_time_entries_update",
        title="Update time entry",
        operation_id="putWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
        body_model=TimeEntryUpdate,
    )

    @server.tool(
        name="clockify_time_entries_update",
        annotations=tool_annotations("clockify_time_entries_update"),
    )
    async def clockify_time_entries_update(
        time_entry_id: str,
        body: TimeEntryUpdate,
        workspace_id: str | None = None,
    ) -> WriteResult:
        """Replace a time entry (PUT: send every field you want to keep)."""
        return await update.execute(
            path_args={
                "workspaceId": update.workspace(workspace_id),
                "timeEntryId": time_entry_id,
            },
            body=body,
        )

    duplicate = RoutineOp(
        deps,
        tool_name="clockify_time_entries_duplicate",
        title="Duplicate time entry",
        operation_id="postWorkspacesWorkspaceIdUserUserIdTimeEntriesTimeEntryIdDuplicate",
    )

    @server.tool(
        name="clockify_time_entries_duplicate",
        annotations=tool_annotations("clockify_time_entries_duplicate"),
    )
    async def clockify_time_entries_duplicate(
        user_id: str,
        time_entry_id: str,
        workspace_id: str | None = None,
    ) -> WriteResult:
        """Duplicate an existing time entry for a user."""
        return await duplicate.execute(
            path_args={
                "workspaceId": duplicate.workspace(workspace_id),
                "userId": user_id,
                "timeEntryId": time_entry_id,
            },
        )

    stop_timer = RoutineOp(
        deps,
        tool_name="clockify_time_entries_stop_timer",
        title="Stop running timer",
        operation_id="patchWorkspacesWorkspaceIdUserUserIdTimeEntries",
    )

    @server.tool(
        name="clockify_time_entries_stop_timer",
        annotations=tool_annotations("clockify_time_entries_stop_timer"),
    )
    async def clockify_time_entries_stop_timer(
        user_id: str,
        end: str,
        workspace_id: str | None = None,
    ) -> WriteResult:
        """Stop the user's running timer at `end` (ISO 8601 UTC)."""
        return await stop_timer.execute(
            path_args={
                "workspaceId": stop_timer.workspace(workspace_id),
                "userId": user_id,
            },
            body={"end": end},
        )

    mark_invoiced = GuardedOp(
        deps,
        tool_name="clockify_time_entries_mark_invoiced",
        title="Mark time entries invoiced",
        operation_id="patchWorkspacesWorkspaceIdTimeEntriesInvoiced",
    )

    async def prepare_mark_invoiced(
        time_entry_ids: list[str],
        invoiced: bool,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        ids = enforce_bulk_caps(tuple(time_entry_ids))
        return await mark_invoiced.prepare(
            arguments={
                "time_entry_ids": list(ids),
                "invoiced": invoiced,
                "workspace_id": workspace_id,
            },
            path_args={"workspaceId": mark_invoiced.workspace(workspace_id)},
            body={"timeEntryIds": list(ids), "invoiced": invoiced},
            scope=f"{len(ids)} time entries",
        )

    def ask_mark_invoiced(
        prepared: Annotated[PreparedWrite, Resolve(prepare_mark_invoiced)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_entries_mark_invoiced",
        annotations=tool_annotations("clockify_time_entries_mark_invoiced"),
    )
    async def clockify_time_entries_mark_invoiced(
        time_entry_ids: list[str],
        invoiced: bool,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_mark_invoiced)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_mark_invoiced)],
    ) -> WriteResult:
        """Set the invoiced flag on a set of time entries (billing state)."""
        return await mark_invoiced.run(prepared, approval)

    bulk_update = GuardedOp(
        deps,
        tool_name="clockify_time_entries_bulk_update_for_user",
        title="Bulk replace user's time entries",
        operation_id="putWorkspacesWorkspaceIdUserUserIdTimeEntries",
    )

    async def prepare_bulk_update(
        user_id: str,
        entries: list[dict[str, Any]],
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        if not entries:
            raise ValueError("entries must not be empty")
        enforce_bulk_caps(tuple(str(index) for index in range(len(entries))))
        return await bulk_update.prepare(
            arguments={
                "user_id": user_id,
                "entries": entries,
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": bulk_update.workspace(workspace_id),
                "userId": user_id,
            },
            body=entries,
            scope=f"{len(entries)} time entries",
        )

    def ask_bulk_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_bulk_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_entries_bulk_update_for_user",
        annotations=tool_annotations("clockify_time_entries_bulk_update_for_user"),
    )
    async def clockify_time_entries_bulk_update_for_user(
        user_id: str,
        entries: list[dict[str, Any]],
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_bulk_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_bulk_update)],
    ) -> WriteResult:
        """Replace ALL of a user's time entries with this list (bulk PUT)."""
        return await bulk_update.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_time_entries_delete",
        title="Delete time entry",
        operation_id="deleteWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
    )

    async def prepare_delete(time_entry_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"time_entry_id": time_entry_id, "workspace_id": workspace_id},
            path_args={
                "workspaceId": delete.workspace(workspace_id),
                "timeEntryId": time_entry_id,
            },
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_entries_delete",
        annotations=tool_annotations("clockify_time_entries_delete"),
    )
    async def clockify_time_entries_delete(
        time_entry_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete one time entry. NOT reversible."""
        return await delete.run(prepared, approval)

    delete_all = GuardedOp(
        deps,
        tool_name="clockify_time_entries_delete_all_for_user",
        title="Delete user's time entries",
        operation_id="deleteMany",
    )

    async def prepare_delete_all(
        user_id: str,
        time_entry_ids: list[str],
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        ids = enforce_bulk_caps(tuple(time_entry_ids))
        if not ids:
            raise ValueError("time_entry_ids must not be empty")
        return await delete_all.prepare(
            arguments={
                "user_id": user_id,
                "time_entry_ids": list(ids),
                "workspace_id": workspace_id,
            },
            path_args={
                "workspaceId": delete_all.workspace(workspace_id),
                "userId": user_id,
            },
            query={"time_entry_ids": list(ids)},
            scope=f"{len(ids)} time entries",
        )

    def ask_delete_all(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete_all)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_time_entries_delete_all_for_user",
        annotations=tool_annotations("clockify_time_entries_delete_all_for_user"),
    )
    async def clockify_time_entries_delete_all_for_user(
        user_id: str,
        time_entry_ids: list[str],
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete_all)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete_all)],
    ) -> WriteResult:
        """Delete a set of a user's time entries by exact IDs. NOT reversible."""
        return await delete_all.run(prepared, approval)
