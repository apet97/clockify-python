"""Expense categories resource: explicit methods over the expense-category operations."""

from collections.abc import Mapping
from typing import Any

from clockify.models import (
    ExpenseCategoriesDtoV1,
    ExpenseCategoryDtoV1,
    ExpenseCategoryRequest,
    ExpenseCategoryStatusRequest,
)
from clockify.operations.expense_categories import (
    EXPENSE_CATEGORIES_CREATE,
    EXPENSE_CATEGORIES_DELETE,
    EXPENSE_CATEGORIES_LIST,
    EXPENSE_CATEGORIES_UPDATE,
    EXPENSE_CATEGORIES_UPDATE_STATUS,
)
from clockify.resources._base import ResourceBase


class ExpenseCategoriesResource(ResourceBase):
    async def create(
        self,
        body: "ExpenseCategoryRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ExpenseCategoryDtoV1:
        validated = self._coerce(body, ExpenseCategoryRequest)
        response = await self._call(
            EXPENSE_CATEGORIES_CREATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(EXPENSE_CATEGORIES_CREATE, response, ExpenseCategoryDtoV1)

    async def delete(self, category_id: str, *, workspace_id: str | None = None) -> None:
        """The category must be archived first (via `update_status`); ACTIVE is rejected."""
        await self._call(
            EXPENSE_CATEGORIES_DELETE,
            path={"workspaceId": self._workspace(workspace_id), "categoryId": category_id},
        )
        return None

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        archived: bool | None = None,
        name: str | None = None,
    ) -> ExpenseCategoriesDtoV1:
        """Returns the `{categories, count}` envelope; items live under `categories`."""
        response = await self._call(
            EXPENSE_CATEGORIES_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
                "archived": archived,
                "name": name,
            },
        )
        return self._adapt(EXPENSE_CATEGORIES_LIST, response, ExpenseCategoriesDtoV1)

    async def update(
        self,
        category_id: str,
        body: "ExpenseCategoryRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ExpenseCategoryDtoV1:
        """Full replacement: resend the complete document; omitted fields reset."""
        validated = self._coerce(body, ExpenseCategoryRequest)
        response = await self._call(
            EXPENSE_CATEGORIES_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "categoryId": category_id},
            body=validated,
        )
        return self._adapt(EXPENSE_CATEGORIES_UPDATE, response, ExpenseCategoryDtoV1)

    async def update_status(
        self,
        category_id: str,
        body: "ExpenseCategoryStatusRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ExpenseCategoryDtoV1:
        validated = self._coerce(body, ExpenseCategoryStatusRequest)
        response = await self._call(
            EXPENSE_CATEGORIES_UPDATE_STATUS,
            path={"workspaceId": self._workspace(workspace_id), "categoryId": category_id},
            body=validated,
        )
        return self._adapt(EXPENSE_CATEGORIES_UPDATE_STATUS, response, ExpenseCategoryDtoV1)
