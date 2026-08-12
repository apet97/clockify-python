# pyright: reportUnusedFunction=false
"""Raw read tools: time_off_balance_assignments (1 read)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(
        name="clockify_time_off_balance_assignments_get_for_user_and_policy",
        annotations=READ_ANNOTATIONS,
    )
    async def clockify_time_off_balance_assignments_get_for_user_and_policy(
        user_id: str,
        policy_id: str,
        workspace_id: str | None = None,
    ) -> ReadResult:
        """Get the time-off balance assignment for one user under one policy."""
        return await raw_read(
            client,
            "getBalanceAssignmentsForUserAndPolicy",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "userId": user_id,
                "policyId": policy_id,
            },
        )
