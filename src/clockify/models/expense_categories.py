"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class ExpenseCategoriesDtoV1(ClockifyResponseModel):
    """Expense categories list response."""

    categories: list[ExpenseCategoryDtoV1] | None = None
    count: int | None = None


class ExpenseCategoryDtoV1(ClockifyResponseModel):
    """Represents an expense category."""

    archived: bool | None = None
    has_unit_price: bool | None = Field(default=None, alias="hasUnitPrice")
    id: str | None = None
    name: str | None = None
    price_in_cents: int | None = Field(default=None, alias="priceInCents")
    unit: str | None = None
    workspace_id: str | None = Field(default=None, alias="workspaceId")
    status: str | None = None


class ExpenseCategoryRequest(ClockifyRequestModel):
    """Request body for adding or updating an expense category."""

    has_unit_price: bool | None = Field(default=None, alias="hasUnitPrice")
    name: str
    price_in_cents: int | None = Field(default=None, alias="priceInCents")
    unit: str | None = None


class ExpenseCategoryStatusRequest(ClockifyRequestModel):
    """Request body for archiving or unarchiving an expense category."""

    archived: bool
