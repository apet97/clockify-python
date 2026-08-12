# pyright: reportUnusedFunction=false
"""Raw read tools: time_off_balances (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_time_off_balances_list_for_policy", annotations=READ_ANNOTATIONS)
    async def clockify_time_off_balances_list_for_policy(
        policy_id: str,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort: str | None = None,
        sort_order: str | None = None,
    ) -> ReadResult:
        """List time-off balances for one policy. Items arrive under the `balances` key."""
        return await raw_read(
            client,
            "getBalancesForPolicy",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "policyId": policy_id,
            },
            query={
                "page": page,
                "page_size": page_size,
                "sort": sort,
                "sort_order": sort_order,
            },
        )

    @server.tool(name="clockify_time_off_balances_list_for_user", annotations=READ_ANNOTATIONS)
    async def clockify_time_off_balances_list_for_user(
        user_id: str,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort: str | None = None,
        sort_order: str | None = None,
    ) -> ReadResult:
        """List time-off balances for one user across policies. Items arrive under
        the `balances` key."""
        return await raw_read(
            client,
            "getBalanceForUser",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "userId": user_id,
            },
            query={
                "page": page,
                "page_size": page_size,
                "sort": sort,
                "sort_order": sort_order,
            },
        )
