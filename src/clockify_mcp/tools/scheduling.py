# pyright: reportUnusedFunction=false
"""Raw read tools: scheduling (5 reads)."""

from typing import Any

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(
        name="clockify_scheduling_get_filtered_user_capacity", annotations=READ_ANNOTATIONS
    )
    async def clockify_scheduling_get_filtered_user_capacity(
        body: dict[str, Any], workspace_id: str | None = None
    ) -> ReadResult:
        """Non-mutating POST search for user capacity totals
        (UserCapacityTotalsRequest body); returns a bare array of UserCapacityTotal."""
        return await raw_read(
            client,
            "getUsersCapacityTotals",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )

    @server.tool(name="clockify_scheduling_get_project_totals", annotations=READ_ANNOTATIONS)
    async def clockify_scheduling_get_project_totals(
        project_id: str,
        workspace_id: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> ReadResult:
        """Get scheduled-assignment totals for one project. `start` and `end` are
        required by live Clockify; the request 400s without them."""
        return await raw_read(
            client,
            "getScheduledAssignmentsOnProject",
            path={"workspaceId": workspace_of(client, workspace_id), "projectId": project_id},
            query={"start": start, "end": end},
        )

    @server.tool(name="clockify_scheduling_get_user_capacity", annotations=READ_ANNOTATIONS)
    async def clockify_scheduling_get_user_capacity(
        user_id: str,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> ReadResult:
        """Get one user's capacity totals. `start` and `end` (yyyy-MM-ddThh:mm:ssZ)
        are required; paginated envelope with item array totalHoursPerDay."""
        return await raw_read(
            client,
            "getUserCapacityTotal",
            path={"workspaceId": workspace_of(client, workspace_id), "userId": user_id},
            query={"page": page, "page_size": page_size, "start": start, "end": end},
        )

    @server.tool(name="clockify_scheduling_list_assignments", annotations=READ_ANNOTATIONS)
    async def clockify_scheduling_list_assignments(
        workspace_id: str | None = None,
        name: str | None = None,
        start: str | None = None,
        end: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List all scheduling assignments. `start` and `end` query params are
        required by live Clockify."""
        return await raw_read(
            client,
            "getAllSchedulingAssignments",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "name": name,
                "start": start,
                "end": end,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )

    @server.tool(name="clockify_scheduling_list_project_totals", annotations=READ_ANNOTATIONS)
    async def clockify_scheduling_list_project_totals(
        body: dict[str, Any], workspace_id: str | None = None
    ) -> ReadResult:
        """Non-mutating POST search for per-project assignment totals
        (ProjectTotalsRequest body). Body REQUIRES start and end; accepted keys are
        camelCase only [end, page, pageSize, search, start, statusFilter]. There is
        no projectId field — a sent projectId is silently dropped and ALL projects
        are returned; use clockify_scheduling_get_project_totals for one project."""
        return await raw_read(
            client,
            "getScheduledAssignmentsPerProject",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )
