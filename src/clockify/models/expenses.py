"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import ExpenseCategoryDto, ProjectInfoDto, TaskInfoDto


class ExpenseCreateRequest(ClockifyRequestModel):
    """Multipart form-data request for creating an expense."""

    amount: float
    billable: bool | None = None
    category_id: str = Field(alias="categoryId")
    date: str
    file: bytes | None = None
    notes: str | None = None
    project_id: str | None = Field(default=None, alias="projectId")
    task_id: str | None = Field(default=None, alias="taskId")
    user_id: str = Field(alias="userId")


class ExpenseDailyTotalsDtoV1(ClockifyResponseModel):
    """Represents an expense daily total data transfer object."""

    date: str | None = None
    date_as_instant: str | None = Field(default=None, alias="dateAsInstant")
    total: float | None = None


class ExpenseDtoV1(ClockifyResponseModel):
    """Represents an expense object."""

    billable: bool | None = None
    category_id: str | None = Field(default=None, alias="categoryId")
    date: str | None = None
    file_id: str | None = Field(default=None, alias="fileId")
    id: str | None = None
    locked: bool | None = None
    notes: str | None = None
    project_id: str | None = Field(default=None, alias="projectId")
    quantity: float | None = None
    task_id: str | None = Field(default=None, alias="taskId")
    total: float | None = None
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class ExpenseHydratedDtoV1(ClockifyResponseModel):
    """Hydrated expense row returned by the workspace expenses list. Carries nested category/project/task objects and fileName instead of the flat categoryId/projectId/taskId that ExpenseDtoV1 exposes."""

    billable: bool | None = None
    category: ExpenseCategoryDto | None = None
    date: str | None = None
    file_id: str | None = Field(default=None, alias="fileId")
    file_name: str | None = Field(default=None, alias="fileName")
    id: str | None = None
    locked: bool | None = None
    notes: str | None = None
    project: ProjectInfoDto | None = None
    quantity: float | None = None
    task: TaskInfoDto | None = None
    total: float | None = None
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class ExpenseUpdateRequest(ClockifyRequestModel):
    """Multipart form-data request for updating an expense."""

    amount: float
    billable: bool | None = None
    category_id: str = Field(alias="categoryId")
    change_fields: list[
        Literal[
            "USER", "DATE", "PROJECT", "TASK", "CATEGORY", "NOTES", "AMOUNT", "BILLABLE", "FILE"
        ]
    ] = Field(alias="changeFields")
    date: str
    file: bytes | None = None
    notes: str | None = None
    project_id: str | None = Field(default=None, alias="projectId")
    task_id: str | None = Field(default=None, alias="taskId")
    user_id: str = Field(alias="userId")


class ExpenseWeeklyTotalsDtoV1(ClockifyResponseModel):
    """Represents an expense weekly total data transfer object."""

    date: str | None = None
    total: float | None = None


class ExpensesWithCountDtoV1(ClockifyResponseModel):
    """Represents an expense with count data transfer object."""

    count: int | None = None
    expenses: list[ExpenseHydratedDtoV1] | None = None


class WorkspaceExpensesDtoV1(ClockifyResponseModel):
    """Response returned by the workspace expenses endpoint."""

    daily_totals: list[ExpenseDailyTotalsDtoV1] | None = Field(default=None, alias="dailyTotals")
    expenses: ExpensesWithCountDtoV1 | None = None
    weekly_totals: list[ExpenseWeeklyTotalsDtoV1] | None = Field(default=None, alias="weeklyTotals")
