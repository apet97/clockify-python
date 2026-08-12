# pyright: reportUnusedFunction=false
"""Raw read tools: holidays (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_holidays_list", annotations=READ_ANNOTATIONS)
    async def clockify_holidays_list(
        workspace_id: str | None = None,
        assigned_to: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List workspace holidays (bare array). `page_size` max 200; there is no
        single-holiday GET route, so scan this list to find one."""
        return await raw_read(
            client,
            "getWorkspaceHolidays",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={"assigned_to": assigned_to, "page": page, "page_size": page_size},
        )

    @server.tool(name="clockify_holidays_list_in_period", annotations=READ_ANNOTATIONS)
    async def clockify_holidays_list_in_period(
        workspace_id: str | None = None,
        assigned_to: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> ReadResult:
        """List holidays in a period. Live Clockify requires all of `assigned_to`,
        `start`, and `end` (yyyy-MM-ddThh:mm:ssZ); `assigned_to` must be a USER id —
        a group id can produce a misleading 403."""
        return await raw_read(
            client,
            "getWorkspaceHolidaysInPeriod",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={"assigned_to": assigned_to, "start": start, "end": end},
        )
