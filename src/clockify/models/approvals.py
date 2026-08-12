"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import (
    DayOfWeek,
    ExpenseCategoryDto,
    ProjectInfoDto,
    RateDto,
    TaskInfoDto,
)

# Approval period. It must match the workspace approval period setting.
ApprovalPeriod = Literal["WEEKLY", "SEMI_MONTHLY", "MONTHLY"]


class ApprovalRequestCreatorDtoV1(ClockifyResponseModel):
    """Represents approval request creator object."""

    user_email: str | None = Field(default=None, alias="userEmail")
    user_id: str | None = Field(default=None, alias="userId")
    user_name: str | None = Field(default=None, alias="userName")


class ApprovalRequestDtoV1(ClockifyResponseModel):
    """Represents a valid approval request data transfer object."""

    creator: ApprovalRequestCreatorDtoV1 | None = None
    date_range: DateRangeDto | None = Field(default=None, alias="dateRange")
    id: str | None = None
    owner: ApprovalRequestOwnerDtoV1 | None = None
    status: ApprovalRequestStatusDtoV1 | None = None
    type: str | None = None
    workspace_id: str | None = Field(default=None, alias="workspaceId")


ApprovalRequestFilterState = Literal["PENDING", "APPROVED", "WITHDRAWN_APPROVAL"]


class ApprovalRequestListItem(ClockifyResponseModel):
    approval_request: ApprovalRequestDtoV1 | None = Field(default=None, alias="approvalRequest")
    approved_time: DurationString | None = Field(default=None, alias="approvedTime")
    billable_amount: float | None = Field(default=None, alias="billableAmount")
    billable_time: DurationString | None = Field(default=None, alias="billableTime")
    break_time: DurationString | None = Field(default=None, alias="breakTime")
    cost_amount: float | None = Field(default=None, alias="costAmount")
    entries: list[TimeEntryInfoDto] | None = None
    expense_total: float | None = Field(default=None, alias="expenseTotal")
    expenses: list[ExpenseHydratedDto] | None = None
    pending_time: DurationString | None = Field(default=None, alias="pendingTime")
    tracked_time: DurationString | None = Field(default=None, alias="trackedTime")


class ApprovalRequestOwnerDtoV1(ClockifyResponseModel):
    """Represents approval request owner object."""

    start_of_week: DayOfWeek | None = Field(default=None, alias="startOfWeek")
    time_zone: str | None = Field(default=None, alias="timeZone")
    user_id: str | None = Field(default=None, alias="userId")
    user_name: str | None = Field(default=None, alias="userName")


ApprovalRequestSortColumn = Literal["ID", "USER_ID", "START", "UPDATED_AT"]

ApprovalRequestState = Literal[
    "PENDING", "APPROVED", "WITHDRAWN_SUBMISSION", "WITHDRAWN_APPROVAL", "REJECTED"
]


class ApprovalRequestStatusDtoV1(ClockifyResponseModel):
    """Represents approval request status object."""

    note: str | None = None
    state: ApprovalRequestState | None = None
    updated_at: str | None = Field(default=None, alias="updatedAt")
    updated_by: str | None = Field(default=None, alias="updatedBy")
    updated_by_user_name: str | None = Field(default=None, alias="updatedByUserName")


ApprovalRequestType = Literal["TIMESHEET", "EXPENSE", "TIMESHEET_AND_EXPENSE"]


class CreateApprovalRequestNoType(ClockifyRequestModel):
    period: Literal["WEEKLY", "SEMI_MONTHLY", "MONTHLY"] | None = None
    period_start: str = Field(alias="periodStart")


class CustomFieldValueDto(ClockifyResponseModel):
    """Represents a custom field value object."""

    custom_field_id: str | None = Field(default=None, alias="customFieldId")
    source_type: Literal["WORKSPACE", "PROJECT", "TIMEENTRY"] | None = Field(
        default=None, alias="sourceType"
    )
    time_entry_id: str | None = Field(default=None, alias="timeEntryId")
    value: Any | None = None


class DateRangeDto(ClockifyResponseModel):
    """Represents date range object."""

    end: str | None = None
    start: str | None = None


DurationString = str


class ExpenseHydratedDto(ClockifyResponseModel):
    """Represents an expense hydrated data transfer object."""

    approval_request_id: str | None = Field(default=None, alias="approvalRequestId")
    approval_status: str | None = Field(default=None, alias="approvalStatus")
    billable: bool | None = None
    category: ExpenseCategoryDto | None = None
    currency: str | None = None
    date: str | None = None
    detailed_approval_status: str | None = Field(default=None, alias="detailedApprovalStatus")
    file_id: str | None = Field(default=None, alias="fileId")
    file_name: str | None = Field(default=None, alias="fileName")
    file_url: str | None = Field(default=None, alias="fileUrl")
    id: str | None = None
    locked: bool | None = None
    notes: str | None = None
    project: ProjectInfoDto | None = None
    quantity: float | None = None
    task: TaskInfoDto | None = None
    total: float | None = None
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class SubmitApprovalRequestRequest(ClockifyRequestModel):
    period: ApprovalPeriod
    period_start: str = Field(alias="periodStart")


class TagDto(ClockifyResponseModel):
    """Represents a tag object."""

    archived: bool | None = None
    id: str | None = None
    name: str | None = None
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class TimeEntryInfoDto(ClockifyResponseModel):
    """Represents a time entry info data transfer object."""

    approval_request_id: str | None = Field(default=None, alias="approvalRequestId")
    billable: bool | None = None
    cost_rate: RateDto | None = Field(default=None, alias="costRate")
    custom_field_values: list[CustomFieldValueDto] | None = Field(
        default=None, alias="customFieldValues"
    )
    description: str | None = None
    hourly_rate: RateDto | None = Field(default=None, alias="hourlyRate")
    id: str | None = None
    is_locked: bool | None = Field(default=None, alias="isLocked")
    project: ProjectInfoDto | None = None
    tags: list[TagDto] | None = None
    task: TaskInfoDto | None = None
    time_interval: TimeIntervalDto | None = Field(default=None, alias="timeInterval")
    type: TimeEntryType | None = None


TimeEntryType = Literal["REGULAR", "BREAK", "HOLIDAY", "TIME_OFF"]


class TimeIntervalDto(ClockifyResponseModel):
    """Represents a time interval object."""

    duration: DurationString | None = None
    end: str | None = None
    offset_end: int | None = Field(default=None, alias="offsetEnd")
    offset_start: int | None = Field(default=None, alias="offsetStart")
    start: str | None = None
    time_zone: str | None = Field(default=None, alias="timeZone")
    zoned_end: str | None = Field(default=None, alias="zonedEnd")
    zoned_start: str | None = Field(default=None, alias="zonedStart")


class UpdateApprovalRequestRequest(ClockifyRequestModel):
    note: str | None = None
    state: ApprovalRequestState
