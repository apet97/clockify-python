"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class RateUpdateRequest(ClockifyRequestModel):
    amount: int
    since: str | None = None


class Task(ClockifyResponseModel):
    """Represents a Clockify task on a project."""

    active: bool | None = None
    assignee_id: str | None = Field(default=None, alias="assigneeId")
    assignee_ids: list[str] | None = Field(default=None, alias="assigneeIds")
    billable: bool
    budget_estimate: int | None = Field(default=None, alias="budgetEstimate")
    cost_rate: TasksRateDtoV1 | None = Field(default=None, alias="costRate")
    duration: str | None = None
    estimate: str | None = None
    hourly_rate: TasksRateDtoV1 | None = Field(default=None, alias="hourlyRate")
    id: str
    name: str
    project_id: str = Field(alias="projectId")
    status: TaskStatus
    user_group_ids: list[str] | None = Field(default=None, alias="userGroupIds")


class TaskCreateRequest(ClockifyRequestModel):
    assignee_id: str | None = Field(default=None, alias="assigneeId")
    assignee_ids: list[str] | None = Field(default=None, alias="assigneeIds")
    billable: bool | None = None
    budget_estimate: int | None = Field(default=None, alias="budgetEstimate")
    estimate: str | None = None
    id: str | None = None
    name: str
    status: TaskStatus | None = None
    user_group_ids: list[str] | None = Field(default=None, alias="userGroupIds")


# Represents task status.
TaskStatus = Literal["ACTIVE", "DONE", "ALL"]


class TaskUpdateRequest(ClockifyRequestModel):
    assignee_id: str | None = Field(default=None, alias="assigneeId")
    assignee_ids: list[str] | None = Field(default=None, alias="assigneeIds")
    billable: bool | None = None
    budget_estimate: int | None = Field(default=None, alias="budgetEstimate")
    estimate: str | None = None
    name: str
    status: TaskStatus | None = None
    user_group_ids: list[str] | None = Field(default=None, alias="userGroupIds")


class TasksRateDtoV1(ClockifyResponseModel):
    """Represents hourly or cost rate object."""

    amount: int | None = None
    currency: str | None = None
