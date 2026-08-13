# pyright: reportUnusedFunction=false
"""Raw read tools: time_off_policies (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_time_off_policies_get", annotations=READ_ANNOTATIONS)
    async def clockify_time_off_policies_get(
        policy_id: str, workspace_id: str | None = None
    ) -> ReadResult:
        """Get one time-off policy by ID."""
        return await raw_read(
            client,
            "getTimeOffPolicy",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "policyId": policy_id,
            },
        )

    @server.tool(name="clockify_time_off_policies_list", annotations=READ_ANNOTATIONS)
    async def clockify_time_off_policies_list(
        workspace_id: str | None = None,
        page: str | None = None,
        page_size: int | None = None,
        name: str | None = None,
        status: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
    ) -> ReadResult:
        """List time-off policies on the workspace, filterable by name and status."""
        return await raw_read(
            client,
            "getTimeOffPolicies",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "page": page,
                "page_size": page_size,
                "name": name,
                "status": status,
                "sort_column": sort_column,
                "sort_order": sort_order,
            },
        )
