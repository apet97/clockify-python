# pyright: reportUnusedFunction=false
"""Raw read tools: expenses (2 reads; receipt download is binary and SDK-only)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_expenses_list", annotations=READ_ANNOTATIONS)
    async def clockify_expenses_list(
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        user_id: str | None = None,
    ) -> ReadResult:
        """List workspace expenses. Items live in a double-nested `expenses.expenses[]`
        envelope (with dailyTotals/weeklyTotals). Money in responses is MINOR units
        (cents). Server ignores date filters — filter client-side."""
        return await raw_read(
            client,
            "getWorkspaceExpenses",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={"page": page, "page_size": page_size, "user_id": user_id},
        )

    @server.tool(name="clockify_expenses_get", annotations=READ_ANNOTATIONS)
    async def clockify_expenses_get(expense_id: str, workspace_id: str | None = None) -> ReadResult:
        """Get one expense by ID. Response `total` is MINOR units (cents)."""
        return await raw_read(
            client,
            "getExpenseById",
            path={"workspaceId": workspace_of(client, workspace_id), "expenseId": expense_id},
        )
