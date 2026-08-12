# pyright: reportUnusedFunction=false
"""Raw read tools: shared_reports (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.errors import ToolError
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_shared_reports_list", annotations=READ_ANNOTATIONS)
    async def clockify_shared_reports_list(
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        shared_reports_filter: str | None = None,
    ) -> ReadResult:
        """List saved shared reports (reports host). `shared_reports_filter` enum:
        ALL, ALL_ADMIN, CREATED_BY_ME, SHARED_WITH_ME (default ALL)."""
        return await raw_read(
            client,
            "getWorkspacesWorkspaceIdSharedReports",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "page": page,
                "page_size": page_size,
                "shared_reports_filter": shared_reports_filter,
            },
        )

    @server.tool(name="clockify_shared_reports_view_public", annotations=READ_ANNOTATIONS)
    async def clockify_shared_reports_view_public(
        shared_report_id: str,
        format: str = "JSON",
        date_range_start: str | None = None,
        date_range_end: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """View a shared report's RENDERED data (no workspaceId in the path).
        `format` must be JSON or CSV; JSON returns {totals, donutChart, groupTotals,
        groupOne, filters}. `sort_column` is validated against the report type
        (unknown column 400s)."""
        normalized = format.upper()
        if normalized not in ("JSON", "CSV"):
            raise ToolError("format must be JSON or CSV; PDF/XLSX are SDK-only")
        return await raw_read(
            client,
            "getSharedReportsSharedReportId",
            path={"sharedReportId": shared_report_id},
            query={
                "export_type": normalized,
                "date_range_start": date_range_start,
                "date_range_end": date_range_end,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )
