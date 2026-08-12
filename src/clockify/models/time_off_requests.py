"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class ChangeTimeOffRequestStatusRequest(ClockifyRequestModel):
    note: str | None = None
    status: Literal["APPROVED", "REJECTED"]


class CreateTimeOffRequest(ClockifyRequestModel):
    note: str | None = None
    time_off_period: TimeOffRequestPeriodV1Request = Field(alias="timeOffPeriod")


# Represents the half day period.
HalfDayPeriod = Literal["FIRST_HALF", "SECOND_HALF", "NOT_DEFINED"]


class Period(ClockifyResponseModel):
    """Represents a period with date-time start and end values."""

    end: str | None = None
    start: str | None = None


class PeriodV1Request(ClockifyRequestModel):
    """Represents period of time off request including start and end date."""

    days: int | None = None
    end: str | None = None
    start: str | None = None


RequestStatusType = Literal["PENDING", "APPROVED", "REJECTED", "ALL"]


class TimeOffRequestDto(ClockifyResponseModel):
    """Represents a time off request response."""

    balance_diff: float | None = Field(default=None, alias="balanceDiff")
    created_at: str | None = Field(default=None, alias="createdAt")
    id: str | None = None
    note: str | None = None
    policy_id: str | None = Field(default=None, alias="policyId")
    status: TimeOffRequestStatus | None = None
    time_off_period: TimeOffRequestPeriodDto | None = Field(default=None, alias="timeOffPeriod")
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class TimeOffRequestFullV1Dto(ClockifyResponseModel):
    """Represents a full time off request response."""

    balance: float | None = None
    balance_diff: float | None = Field(default=None, alias="balanceDiff")
    created_at: str | None = Field(default=None, alias="createdAt")
    id: str | None = None
    note: str | None = None
    policy_id: str | None = Field(default=None, alias="policyId")
    policy_name: str | None = Field(default=None, alias="policyName")
    requester_user_id: str | None = Field(default=None, alias="requesterUserId")
    requester_user_name: str | None = Field(default=None, alias="requesterUserName")
    status: TimeOffRequestStatus | None = None
    time_off_period: TimeOffRequestPeriodDto | None = Field(default=None, alias="timeOffPeriod")
    time_unit: TimeUnit | None = Field(default=None, alias="timeUnit")
    user_email: str | None = Field(default=None, alias="userEmail")
    user_id: str | None = Field(default=None, alias="userId")
    user_name: str | None = Field(default=None, alias="userName")
    user_time_zone: str | None = Field(default=None, alias="userTimeZone")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class TimeOffRequestPeriodDto(ClockifyResponseModel):
    """Represents the period of the time off request."""

    half_day: bool | None = Field(default=None, alias="halfDay")
    half_day_hours: Period | None = Field(default=None, alias="halfDayHours")
    half_day_period: HalfDayPeriod | None = Field(default=None, alias="halfDayPeriod")
    period: Period | None = None


class TimeOffRequestPeriodV1Request(ClockifyRequestModel):
    """Provide the period you would like to use for creating the time off request. If timeZone isn't set, should be aligned with time zone for user in settings. Can be shifted from user time zone with explicit setting of timeZone."""

    half_day_period: HalfDayPeriod | None = Field(default=None, alias="halfDayPeriod")
    is_half_day: bool | None = Field(default=None, alias="isHalfDay")
    period: PeriodV1Request
    time_off_half_day_period: HalfDayPeriod | None = Field(
        default=None, alias="timeOffHalfDayPeriod"
    )


class TimeOffRequestSearchRequest(ClockifyRequestModel):
    """Filters used to return time off requests on a workspace."""

    end: str | None = None
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    start: str | None = None
    statuses: list[RequestStatusType] | None = None
    user_groups: list[str] | None = Field(default=None, alias="userGroups")
    users: list[str] | None = None


class TimeOffRequestStatus(ClockifyResponseModel):
    """Represents the status of the time off request."""

    changed_at: str | None = Field(default=None, alias="changedAt")
    changed_by_user_id: str | None = Field(default=None, alias="changedByUserId")
    changed_by_user_name: str | None = Field(default=None, alias="changedByUserName")
    changed_for_user_name: str | None = Field(default=None, alias="changedForUserName")
    note: str | None = None
    status_type: RequestStatusType | None = Field(default=None, alias="statusType")


class TimeOffRequestsResponse(ClockifyResponseModel):
    count: int | None = None
    requests: list[TimeOffRequestFullV1Dto] | None = None


# Represents the time unit of the time off request.
TimeUnit = Literal["DAYS", "HOURS"]
