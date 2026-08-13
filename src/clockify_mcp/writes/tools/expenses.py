# pyright: reportUnusedFunction=false
"""Guarded write tools: expenses."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import ExpenseCreateRequest, ExpenseUpdateRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_expenses_create",
        title="Create expense",
        operation_id="createExpense",
        body_model=ExpenseCreateRequest,
    )

    async def prepare_create(
        body: ExpenseCreateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await create.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": create.workspace(workspace_id)},
            body=body,
        )

    def ask_create(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_expenses_create", annotations=tool_annotations("clockify_expenses_create")
    )
    async def clockify_expenses_create(
        body: ExpenseCreateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create an expense. File attachments are not supported through MCP."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_expenses_update",
        title="Update expense",
        operation_id="updateExpense",
        body_model=ExpenseUpdateRequest,
    )

    async def prepare_update(
        expense_id: str, body: ExpenseUpdateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={"expense_id": expense_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id), "expenseId": expense_id},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_expenses_update", annotations=tool_annotations("clockify_expenses_update")
    )
    async def clockify_expenses_update(
        expense_id: str,
        body: ExpenseUpdateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace an expense (PUT). File attachments are not supported through MCP."""
        return await update.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_expenses_delete",
        title="Delete expense",
        operation_id="deleteExpense",
    )

    async def prepare_delete(expense_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"expense_id": expense_id, "workspace_id": workspace_id},
            path_args={"workspaceId": delete.workspace(workspace_id), "expenseId": expense_id},
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_expenses_delete", annotations=tool_annotations("clockify_expenses_delete")
    )
    async def clockify_expenses_delete(
        expense_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete an expense. NOT reversible."""
        return await delete.run(prepared, approval)
