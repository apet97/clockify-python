"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import Currency


class BulkEditTimeEntryRequest(ClockifyRequestModel):
    """LIVE VERIFICATION REVEALED - Field 'end' is mandatory for bulk edits on live system, contrary to single-update documentation."""

    billable: bool | None = None
    description: str | None = None
    end: str
    id: str
    project_id: str | None = Field(default=None, alias="projectId")
    start: str
    task_id: str | None = Field(default=None, alias="taskId")


class CreateTimeEntryRequest(ClockifyRequestModel):
    billable: bool | None = None
    description: str | None = None
    end: str | None = None
    project_id: str | None = Field(default=None, alias="projectId")
    start: str
    tag_ids: list[str] | None = Field(default=None, alias="tagIds")
    task_id: str | None = Field(default=None, alias="taskId")
    type: Literal["REGULAR", "BREAK"] | None = None


class CustomFieldValueDtoV1(ClockifyResponseModel):
    """Represents a list of custom field value objects."""

    custom_field_id: str | None = Field(default=None, alias="customFieldId")
    name: str | None = None
    time_entry_id: str | None = Field(default=None, alias="timeEntryId")
    type: str | None = None
    value: dict[str, Any] | None = None


class DateTimeInterval(ClockifyResponseModel):
    duration: str | None = None
    end: str | None = None
    off_end: int | None = Field(default=None, alias="offEnd")
    off_start: int | None = Field(default=None, alias="offStart")
    start: str | None = None
    time_zone: str | None = Field(default=None, alias="timeZone")
    zoned_end: str | None = Field(default=None, alias="zonedEnd")
    zoned_start: str | None = Field(default=None, alias="zonedStart")


class GetTimeEntriesByIdsRequest(ClockifyRequestModel):
    hydrated: bool | None = None
    time_entry_ids: list[str] = Field(alias="timeEntryIds")


class OpenapiRateDto(ClockifyResponseModel):
    amount: int | None = None
    currency: Currency | None = None


class OpenapiRateDto2(ClockifyResponseModel):
    """Represents hourly rate object."""

    amount: int | None = None
    currency: str | None = None


class TimeEntriesCustomFieldValueDto(ClockifyResponseModel):
    custom_field_id: str | None = Field(default=None, alias="customFieldId")
    name: str | None = None
    time_entry_id: str | None = Field(default=None, alias="timeEntryId")
    type: Literal["WORKSPACE", "PROJECT", "TIMEENTRY"] | None = None
    value: str | None = None


class TimeEntriesTimeEntry(ClockifyResponseModel):
    billable: bool | None = None
    custom_field_values: list[TimeEntriesCustomFieldValueDto] | None = Field(
        default=None, alias="customFieldValues"
    )
    description: str | None = None
    id: str | None = None
    is_locked: bool | None = Field(default=None, alias="isLocked")
    kiosk_id: str | None = Field(default=None, alias="kioskId")
    project_id: str | None = Field(default=None, alias="projectId")
    tag_ids: list[str] | None = Field(default=None, alias="tagIds")
    task_id: str | None = Field(default=None, alias="taskId")
    time_interval: TimeEntriesTimeIntervalDto | None = Field(default=None, alias="timeInterval")
    type: Literal["REGULAR", "BREAK", "HOLIDAY", "TIME_OFF"] | None = None
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class TimeEntriesTimeIntervalDto(ClockifyResponseModel):
    duration: str | None = None
    end: str | None = None
    start: str | None = None


class TimeEntry(ClockifyResponseModel):
    approval_request_id: str | None = Field(default=None, alias="approvalRequestId")
    billable: bool
    cost_rate: OpenapiRateDto | None = Field(default=None, alias="costRate")
    custom_field_values: list[dict[str, Any]] | None = Field(
        default=None, alias="customFieldValues"
    )
    description: str
    hourly_rate: OpenapiRateDto | None = Field(default=None, alias="hourlyRate")
    id: str
    is_locked: bool = Field(alias="isLocked")
    kiosk_id: str | None = Field(default=None, alias="kioskId")
    project_id: str | None = Field(default=None, alias="projectId")
    tag_ids: list[str] | None = Field(default=None, alias="tagIds")
    task_id: str | None = Field(default=None, alias="taskId")
    time_interval: DateTimeInterval = Field(alias="timeInterval")
    type: Literal["REGULAR", "BREAK", "TIMEOFF", "HOLIDAY", "OVERTIME"]
    user_id: str = Field(alias="userId")
    workspace_id: str = Field(alias="workspaceId")


class TimeEntryCreatePropertiesItem(ClockifyRequestModel):
    custom_field_id: str | None = Field(default=None, alias="customFieldId")
    source_type: Literal["WORKSPACE", "PROJECT"] | None = Field(default=None, alias="sourceType")
    value: Any | None = None


class TimeEntryCreate(ClockifyRequestModel):
    billable: bool | None = None
    custom_fields: list[TimeEntryCreatePropertiesItem] | None = Field(
        default=None, alias="customFields"
    )
    description: str | None = None
    end: str | None = None
    project_id: str | None = Field(default=None, alias="projectId")
    start: str
    tag_ids: list[str] | None = Field(default=None, alias="tagIds")
    task_id: str | None = Field(default=None, alias="taskId")
    type: Literal["REGULAR", "BREAK"] | None = None


class TimeEntryDtoImplV1(ClockifyResponseModel):
    billable: bool | None = None
    custom_field_values: list[CustomFieldValueDtoV1] | None = Field(
        default=None, alias="customFieldValues"
    )
    description: str | None = None
    id: str | None = None
    is_locked: bool | None = Field(default=None, alias="isLocked")
    kiosk_id: str | None = Field(default=None, alias="kioskId")
    project_id: str | None = Field(default=None, alias="projectId")
    tag_ids: list[str] | None = Field(default=None, alias="tagIds")
    task_id: str | None = Field(default=None, alias="taskId")
    time_interval: TimeIntervalDtoV1 | None = Field(default=None, alias="timeInterval")
    type: Literal["REGULAR", "BREAK", "HOLIDAY", "TIME_OFF"] | None = None
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class TimeEntryUpdatePropertiesItem(ClockifyRequestModel):
    custom_field_id: str | None = Field(default=None, alias="customFieldId")
    source_type: Literal["WORKSPACE", "PROJECT"] | None = Field(default=None, alias="sourceType")
    value: Any | None = None


class TimeEntryUpdate(ClockifyRequestModel):
    billable: bool | None = None
    custom_fields: list[TimeEntryUpdatePropertiesItem] | None = Field(
        default=None, alias="customFields"
    )
    description: str | None = None
    end: str | None = None
    project_id: str | None = Field(default=None, alias="projectId")
    start: str
    tag_ids: list[str] | None = Field(default=None, alias="tagIds")
    task_id: str | None = Field(default=None, alias="taskId")
    type: Literal["REGULAR", "BREAK"] | None = None


class TimeEntryWithRatesDtoV1(ClockifyResponseModel):
    billable: bool | None = None
    cost_rate: OpenapiRateDto2 | None = Field(default=None, alias="costRate")
    custom_field_values: list[CustomFieldValueDtoV1] | None = Field(
        default=None, alias="customFieldValues"
    )
    description: str | None = None
    hourly_rate: OpenapiRateDto2 | None = Field(default=None, alias="hourlyRate")
    id: str | None = None
    is_locked: bool | None = Field(default=None, alias="isLocked")
    kiosk_id: str | None = Field(default=None, alias="kioskId")
    project_id: str | None = Field(default=None, alias="projectId")
    tag_ids: list[str] | None = Field(default=None, alias="tagIds")
    task_id: str | None = Field(default=None, alias="taskId")
    time_interval: TimeIntervalDtoV1 | None = Field(default=None, alias="timeInterval")
    type: Literal["REGULAR", "BREAK", "HOLIDAY", "TIME_OFF"] | None = None
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class TimeIntervalDtoV1(ClockifyResponseModel):
    """Represents a time interval object."""

    duration: str | None = None
    end: str | None = None
    start: str | None = None
