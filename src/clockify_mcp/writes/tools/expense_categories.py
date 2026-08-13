# pyright: reportUnusedFunction=false
"""Guarded write tools: expense categories."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import ExpenseCategoryRequest, ExpenseCategoryStatusRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_expense_categories_create",
        title="Create expense category",
        operation_id="addExpenseCategory",
        body_model=ExpenseCategoryRequest,
    )

    async def prepare_create(
        body: ExpenseCategoryRequest, workspace_id: str | None = None
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
        name="clockify_expense_categories_create",
        annotations=tool_annotations("clockify_expense_categories_create"),
    )
    async def clockify_expense_categories_create(
        body: ExpenseCategoryRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create an expense category."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_expense_categories_update",
        title="Update expense category",
        operation_id="updateExpenseCategory",
        body_model=ExpenseCategoryRequest,
    )

    async def prepare_update(
        category_id: str, body: ExpenseCategoryRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={"category_id": category_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id), "categoryId": category_id},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_expense_categories_update",
        annotations=tool_annotations("clockify_expense_categories_update"),
    )
    async def clockify_expense_categories_update(
        category_id: str,
        body: ExpenseCategoryRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace an expense category (PUT)."""
        return await update.run(prepared, approval)

    update_status = GuardedOp(
        deps,
        tool_name="clockify_expense_categories_update_status",
        title="Archive expense category",
        operation_id="archiveExpenseCategory",
        body_model=ExpenseCategoryStatusRequest,
    )

    async def prepare_update_status(
        category_id: str, body: ExpenseCategoryStatusRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update_status.prepare(
            arguments={"category_id": category_id, "body": body, "workspace_id": workspace_id},
            path_args={
                "workspaceId": update_status.workspace(workspace_id),
                "categoryId": category_id,
            },
            body=body,
        )

    def ask_update_status(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_expense_categories_update_status",
        annotations=tool_annotations("clockify_expense_categories_update_status"),
    )
    async def clockify_expense_categories_update_status(
        category_id: str,
        body: ExpenseCategoryStatusRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update_status)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update_status)],
    ) -> WriteResult:
        """Archive or unarchive an expense category."""
        return await update_status.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_expense_categories_delete",
        title="Delete expense category",
        operation_id="deleteExpenseCategory",
    )

    async def prepare_delete(category_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"category_id": category_id, "workspace_id": workspace_id},
            path_args={"workspaceId": delete.workspace(workspace_id), "categoryId": category_id},
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_expense_categories_delete",
        annotations=tool_annotations("clockify_expense_categories_delete"),
    )
    async def clockify_expense_categories_delete(
        category_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete an expense category. NOT reversible."""
        return await delete.run(prepared, approval)
