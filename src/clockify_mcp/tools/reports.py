# pyright: reportUnusedFunction=false
"""Raw read tools: reports (5 reads; all JSON-body POST reads on the reports host)."""

from typing import Any

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_reports_attendance", annotations=READ_ANNOTATIONS)
    async def clockify_reports_attendance(
        body: dict[str, Any], workspace_id: str | None = None
    ) -> ReadResult:
        """Generate an attendance report (AttendanceReportRequest body).
        dateRangeStart/dateRangeEnd are wall-clock in the body's timeZone; response
        timestamps are rendered in that timeZone, not UTC Z."""
        return await raw_read(
            client,
            "generateAttendanceReport",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )

    @server.tool(name="clockify_reports_detailed", annotations=READ_ANNOTATIONS)
    async def clockify_reports_detailed(
        body: dict[str, Any], workspace_id: str | None = None
    ) -> ReadResult:
        """Generate a detailed time-entry report (DetailedReportRequest body).
        Envelope item arrays: timeEntries, timeentries, totals. Date ranges are
        wall-clock in the body's timeZone."""
        return await raw_read(
            client,
            "generateDetailedReport",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )

    @server.tool(name="clockify_reports_expense_details", annotations=READ_ANNOTATIONS)
    async def clockify_reports_expense_details(
        workspace_id: str | None = None, body: dict[str, Any] | None = None
    ) -> ReadResult:
        """Generate a detailed expense report (optional ExpenseReportFilterV1 body).
        Money fields keep raw upstream integer units (response totals are MINOR units)."""
        return await raw_read(
            client,
            "generateDetailedReportV1",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )

    @server.tool(name="clockify_reports_summary", annotations=READ_ANNOTATIONS)
    async def clockify_reports_summary(
        body: dict[str, Any], workspace_id: str | None = None
    ) -> ReadResult:
        """Generate a summary report (SummaryReportRequest body). Envelope item
        arrays: groupOne, totals, donutChart. Date ranges are wall-clock in the
        body's timeZone."""
        return await raw_read(
            client,
            "generateSummaryReport",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )

    @server.tool(name="clockify_reports_weekly", annotations=READ_ANNOTATIONS)
    async def clockify_reports_weekly(
        body: dict[str, Any], workspace_id: str | None = None
    ) -> ReadResult:
        """Generate a weekly report (WeeklyReportRequest body). The body MUST use an
        EXACT seven-day dateRangeStart..dateRangeEnd interval or the API rejects it.
        Envelope item arrays: groupOne, totals, totalsByDay, usersWithoutTime."""
        return await raw_read(
            client,
            "generateWeeklyReport",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )
