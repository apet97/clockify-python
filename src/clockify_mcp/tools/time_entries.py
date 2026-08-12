# pyright: reportUnusedFunction=false
"""Raw read tools: time_entries (4 reads)."""

from typing import Any

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_time_entries_get", annotations=READ_ANNOTATIONS)
    async def clockify_time_entries_get(
        time_entry_id: str,
        workspace_id: str | None = None,
        hydrated: bool | None = None,
        consider_duration_format: bool | None = None,
    ) -> ReadResult:
        """Get one time entry by ID. Set `hydrated` for full project/task/tag objects."""
        return await raw_read(
            client,
            "getWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "timeEntryId": time_entry_id,
            },
            query={
                "hydrated": hydrated,
                "consider_duration_format": consider_duration_format,
            },
        )

    @server.tool(name="clockify_time_entries_get_many", annotations=READ_ANNOTATIONS)
    async def clockify_time_entries_get_many(
        body: dict[str, Any],
        workspace_id: str | None = None,
    ) -> ReadResult:
        """Batch-read time entries by ID (non-mutating POST). `body` is a
        GetTimeEntriesByIdsRequest listing the time entry IDs to fetch."""
        return await raw_read(
            client,
            "getMultipleTimeEntries",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )

    @server.tool(name="clockify_time_entries_list_for_user", annotations=READ_ANNOTATIONS)
    async def clockify_time_entries_list_for_user(
        user_id: str,
        workspace_id: str | None = None,
        description: str | None = None,
        start: str | None = None,
        end: str | None = None,
        project: str | None = None,
        task: str | None = None,
        tags: list[str] | None = None,
        project_required: bool | None = None,
        task_required: bool | None = None,
        hydrated: bool | None = None,
        in_progress: bool | None = None,
        get_week_before: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List one user's time entries with filters. The start/end window is
        re-read as wall clock in the account's timezone."""
        return await raw_read(
            client,
            "getWorkspacesWorkspaceIdUserUserIdTimeEntries",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "userId": user_id,
            },
            query={
                "description": description,
                "start": start,
                "end": end,
                "project": project,
                "task": task,
                "tags": tags,
                "project_required": project_required,
                "task_required": task_required,
                "hydrated": hydrated,
                "in_progress": in_progress,
                "get_week_before": get_week_before,
                "page": page,
                "page_size": page_size,
            },
        )

    @server.tool(name="clockify_time_entries_list_in_progress", annotations=READ_ANNOTATIONS)
    async def clockify_time_entries_list_in_progress(
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List currently running (in-progress) time entries on the workspace."""
        return await raw_read(
            client,
            "getWorkspacesWorkspaceIdTimeEntriesStatusInProgress",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={"page": page, "page_size": page_size},
        )
