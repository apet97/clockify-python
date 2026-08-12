"""Expenses resource: explicit methods over the expense operations."""

from collections.abc import Mapping
from typing import Any

from clockify.files import Upload
from clockify.models import (
    ExpenseCreateRequest,
    ExpenseDtoV1,
    ExpenseUpdateRequest,
    WorkspaceExpensesDtoV1,
)
from clockify.operations.expenses import (
    EXPENSES_CREATE,
    EXPENSES_DELETE,
    EXPENSES_DOWNLOAD_RECEIPT,
    EXPENSES_GET,
    EXPENSES_LIST,
    EXPENSES_UPDATE,
)
from clockify.resources._base import ResourceBase
from clockify.response import BinaryResponse


class ExpensesResource(ResourceBase):
    async def create(
        self,
        body: "ExpenseCreateRequest | Mapping[str, Any]",
        *,
        file: Upload | None = None,
        workspace_id: str | None = None,
    ) -> ExpenseDtoV1:
        """Multipart. Request `amount` is MAJOR units (dollars); response `total` is MINOR (cents)."""
        validated = self._coerce(body, ExpenseCreateRequest)
        response = await self._call(
            EXPENSES_CREATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
            files={"file": file} if file is not None else None,
        )
        return self._adapt(EXPENSES_CREATE, response, ExpenseDtoV1)

    async def delete(self, expense_id: str, *, workspace_id: str | None = None) -> None:
        await self._call(
            EXPENSES_DELETE,
            path={"workspaceId": self._workspace(workspace_id), "expenseId": expense_id},
        )
        return None

    async def download_receipt(
        self, expense_id: str, file_id: str, *, workspace_id: str | None = None
    ) -> BinaryResponse:
        response = await self._call(
            EXPENSES_DOWNLOAD_RECEIPT,
            path={
                "workspaceId": self._workspace(workspace_id),
                "expenseId": expense_id,
                "fileId": file_id,
            },
        )
        return response.data

    async def get(self, expense_id: str, *, workspace_id: str | None = None) -> ExpenseDtoV1:
        response = await self._call(
            EXPENSES_GET,
            path={"workspaceId": self._workspace(workspace_id), "expenseId": expense_id},
        )
        return self._adapt(EXPENSES_GET, response, ExpenseDtoV1)

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        user_id: str | None = None,
    ) -> WorkspaceExpensesDtoV1:
        """Double-nested envelope: items at `expenses.expenses[]`; no server-side date filter."""
        response = await self._call(
            EXPENSES_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={"page": page, "page_size": page_size, "user_id": user_id},
        )
        return self._adapt(EXPENSES_LIST, response, WorkspaceExpensesDtoV1)

    async def update(
        self,
        expense_id: str,
        body: "ExpenseUpdateRequest | Mapping[str, Any]",
        *,
        file: Upload | None = None,
        workspace_id: str | None = None,
    ) -> ExpenseDtoV1:
        """Multipart full replacement; `amount` is MAJOR units (dollars) — resend everything."""
        validated = self._coerce(body, ExpenseUpdateRequest)
        response = await self._call(
            EXPENSES_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "expenseId": expense_id},
            body=validated,
            files={"file": file} if file is not None else None,
        )
        return self._adapt(EXPENSES_UPDATE, response, ExpenseDtoV1)
