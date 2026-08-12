# pyright: reportUnusedFunction=false
"""Registration of the five curated read workflows."""

from typing import Any

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.context import ServerConfig
from clockify_mcp.read_capability import WorkflowReadClient
from clockify_mcp.tools._shared import READ_ANNOTATIONS
from clockify_mcp.workflows.doctor import doctor
from clockify_mcp.workflows.review import review_day, review_week
from clockify_mcp.workflows.status import status
from clockify_mcp.workflows.workspace import workspace_overview


def register_workflows(
    server: MCPServer, client: ClockifyClient, config: ServerConfig | None = None
) -> None:
    resolved_config = config or ServerConfig.from_env()
    # F3: workflows get only the read capability, never the full client.
    read_client = WorkflowReadClient(client)

    @server.tool(name="clockify_status", annotations=READ_ANNOTATIONS)
    async def clockify_status() -> dict[str, Any]:
        """Current user, configured/default workspace, and running timers."""
        return await status(read_client)

    @server.tool(name="clockify_workspace_overview", annotations=READ_ANNOTATIONS)
    async def clockify_workspace_overview(workspace_id: str | None = None) -> dict[str, Any]:
        """Workspace identity plus first-page counts of users, projects, and tags."""
        return await workspace_overview(read_client, workspace_id)

    @server.tool(name="clockify_review_day", annotations=READ_ANNOTATIONS)
    async def clockify_review_day(
        day: str,
        timezone_name: str = "UTC",
        user_id: str | None = None,
        workspace_id: str | None = None,
        correlate_projects: bool = False,
    ) -> dict[str, Any]:
        """A user's time entries for one wall-clock day (IANA timezone)."""
        return await review_day(
            read_client,
            day,
            timezone_name=timezone_name,
            user_id=user_id,
            workspace_id=workspace_id,
            correlate_projects=correlate_projects,
        )

    @server.tool(name="clockify_review_week", annotations=READ_ANNOTATIONS)
    async def clockify_review_week(
        start_day: str,
        timezone_name: str = "UTC",
        user_id: str | None = None,
        workspace_id: str | None = None,
    ) -> dict[str, Any]:
        """Entries plus weekly report totals for the exact 7 days from start_day."""
        return await review_week(
            read_client,
            start_day,
            timezone_name=timezone_name,
            user_id=user_id,
            workspace_id=workspace_id,
        )

    @server.tool(name="clockify_doctor", annotations=READ_ANNOTATIONS)
    async def clockify_doctor() -> dict[str, Any]:
        """Diagnose credential/workspace configuration with minimal read calls."""
        return await doctor(read_client, resolved_config)
