"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import DayOfWeek


class AssignmentListItem(ClockifyResponseModel):
    """Represents a scheduled assignment returned by the list endpoint."""

    billable: bool | None = None
    client_id: str | None = Field(default=None, alias="clientId")
    client_name: str | None = Field(default=None, alias="clientName")
    hours_per_day: float | None = Field(default=None, alias="hoursPerDay")
    id: str | None = None
    note: str | None = None
    period: SchedulingDateRangeDto | None = None
    project_archived: bool | None = Field(default=None, alias="projectArchived")
    project_billable: bool | None = Field(default=None, alias="projectBillable")
    project_color: str | None = Field(default=None, alias="projectColor")
    project_id: str | None = Field(default=None, alias="projectId")
    project_name: str | None = Field(default=None, alias="projectName")
    start_time: str | None = Field(default=None, alias="startTime")
    task_id: str | None = Field(default=None, alias="taskId")
    task_name: str | None = Field(default=None, alias="taskName")
    user_id: str | None = Field(default=None, alias="userId")
    user_name: str | None = Field(default=None, alias="userName")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class AssignmentPerDayDto(ClockifyResponseModel):
    """Represents an assignment-per-day object."""

    date: str | None = None
    has_assignment: bool | None = Field(default=None, alias="hasAssignment")


AssignmentSortColumn = Literal["PROJECT", "USER", "ID"]


class ChangeRecurringPeriodRequest(ClockifyRequestModel):
    """Request for changing a recurring assignment period."""

    repeat: bool
    weeks: int


ContainsFilterType = Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"]


class ContainsUserGroupFilterRequestV1(ClockifyRequestModel):
    """Represents a user group filter request object."""

    contains: ContainsFilterType | None = None
    ids: list[str] | None = None
    status: MembershipStatus | None = None


class ContainsUsersFilterRequestV1(ClockifyRequestModel):
    """Represents a user filter request object."""

    contains: ContainsFilterType | None = None
    ids: list[str] | None = None
    source_type: Literal["USER_GROUP"] | None = Field(default=None, alias="sourceType")
    status: MembershipStatus | None = None
    statuses: list[MembershipStatus] | None = None


class CopyAssignmentRequest(ClockifyRequestModel):
    """Request for copying a scheduled assignment."""

    series_update_option: SeriesUpdateOption = Field(alias="seriesUpdateOption")
    user_id: str = Field(alias="userId")


class CreateRecurringAssignmentRequest(ClockifyRequestModel):
    """Request for creating a recurring assignment."""

    billable: bool | None = None
    end: str
    hours_per_day: float = Field(alias="hoursPerDay")
    include_non_working_days: bool | None = Field(default=None, alias="includeNonWorkingDays")
    note: str | None = None
    project_id: str = Field(alias="projectId")
    recurring_assignment: RecurringAssignmentRequestV1 | None = Field(
        default=None, alias="recurringAssignment"
    )
    start: str
    start_time: str | None = Field(default=None, alias="startTime")
    task_id: str | None = Field(default=None, alias="taskId")
    user_id: str = Field(alias="userId")


MembershipStatus = Literal["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"]


class MilestoneDto(ClockifyResponseModel):
    """Represents a milestone object."""

    date: str | None = None
    id: str | None = None
    name: str | None = None
    project_id: str | None = Field(default=None, alias="projectId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class ProjectAssignmentsTotal(ClockifyResponseModel):
    """Represents scheduled assignment totals for a project."""

    assignments: list[AssignmentPerDayDto] | None = None
    client_name: str | None = Field(default=None, alias="clientName")
    milestones: list[MilestoneDto] | None = None
    project_archived: bool | None = Field(default=None, alias="projectArchived")
    project_billable: bool | None = Field(default=None, alias="projectBillable")
    project_color: str | None = Field(default=None, alias="projectColor")
    project_id: str | None = Field(default=None, alias="projectId")
    project_name: str | None = Field(default=None, alias="projectName")
    task_id: str | None = Field(default=None, alias="taskId")
    task_name: str | None = Field(default=None, alias="taskName")
    total_hours: float | None = Field(default=None, alias="totalHours")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class ProjectTotalsRequest(ClockifyRequestModel):
    """Request for scheduled assignments per project."""

    end: str
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    search: str | None = None
    start: str
    status_filter: StatusFilter | None = Field(default=None, alias="statusFilter")


class PublishAssignmentsRequest(ClockifyRequestModel):
    """Request for publishing assignments."""

    end: str
    notify_users: bool | None = Field(default=None, alias="notifyUsers")
    search: str | None = None
    start: str
    user_filter: ContainsUsersFilterRequestV1 | None = Field(default=None, alias="userFilter")
    user_group_filter: ContainsUserGroupFilterRequestV1 | None = Field(
        default=None, alias="userGroupFilter"
    )
    view_type: SchedulingViewType | None = Field(default=None, alias="viewType")


class RecurringAssignmentDto(ClockifyResponseModel):
    """Represents recurring assignment object."""

    repeat: bool | None = None
    series_id: str | None = Field(default=None, alias="seriesId")
    weeks: int | None = None


class RecurringAssignmentRequestV1(ClockifyRequestModel):
    """Recurring assignment settings."""

    repeat: bool | None = None
    weeks: int


class SchedulingAssignment(ClockifyResponseModel):
    """Represents a scheduled assignment."""

    billable: bool | None = None
    exclude_days: list[SchedulingExcludeDay] | None = Field(default=None, alias="excludeDays")
    hours_per_day: float | None = Field(default=None, alias="hoursPerDay")
    id: str | None = None
    include_non_working_days: bool | None = Field(default=None, alias="includeNonWorkingDays")
    note: str | None = None
    period: SchedulingDateRangeDto | None = None
    project_id: str | None = Field(default=None, alias="projectId")
    published: bool | None = None
    recurring: RecurringAssignmentDto | None = None
    start_time: str | None = Field(default=None, alias="startTime")
    task_id: str | None = Field(default=None, alias="taskId")
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class SchedulingDateRangeDto(ClockifyResponseModel):
    """Represents date range object."""

    end: str | None = None
    start: str | None = None


class SchedulingExcludeDay(ClockifyResponseModel):
    """Represents a scheduling excluded day."""

    date: str | None = None
    type: SchedulingExcludeDayType | None = None


SchedulingExcludeDayType = Literal["WEEKEND", "HOLIDAY", "TIME_OFF"]

SchedulingViewType = Literal["PROJECTS", "TEAM", "ALL"]

SeriesUpdateOption = Literal["THIS_ONE", "THIS_AND_FOLLOWING", "ALL"]

StatusFilter = Literal["PUBLISHED", "UNPUBLISHED", "ALL"]


class TotalsPerDayDto(ClockifyResponseModel):
    """Represents total hours per day object."""

    date: str | None = None
    total_hours: float | None = Field(default=None, alias="totalHours")


class UpdateRecurringAssignmentRequest(ClockifyRequestModel):
    """Request for updating a recurring assignment."""

    billable: bool | None = None
    end: str
    hours_per_day: float | None = Field(default=None, alias="hoursPerDay")
    include_non_working_days: bool | None = Field(default=None, alias="includeNonWorkingDays")
    note: str | None = None
    series_update_option: SeriesUpdateOption | None = Field(
        default=None, alias="seriesUpdateOption"
    )
    start: str
    start_time: str | None = Field(default=None, alias="startTime")
    task_id: str | None = Field(default=None, alias="taskId")


class UserCapacityTotal(ClockifyResponseModel):
    """Represents capacity totals for a user."""

    capacity_per_day: float | None = Field(default=None, alias="capacityPerDay")
    total_hours_per_day: list[TotalsPerDayDto] | None = Field(
        default=None, alias="totalHoursPerDay"
    )
    user_id: str | None = Field(default=None, alias="userId")
    user_image: str | None = Field(default=None, alias="userImage")
    user_name: str | None = Field(default=None, alias="userName")
    user_status: str | None = Field(default=None, alias="userStatus")
    working_days: list[DayOfWeek] | str | None = Field(default=None, alias="workingDays")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class UserCapacityTotalsRequest(ClockifyRequestModel):
    """Request for total capacity of users on a workspace."""

    end: str
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    search: str | None = None
    start: str
    status_filter: StatusFilter | None = Field(default=None, alias="statusFilter")
    user_filter: ContainsUsersFilterRequestV1 | None = Field(default=None, alias="userFilter")
    user_group_filter: ContainsUserGroupFilterRequestV1 | None = Field(
        default=None, alias="userGroupFilter"
    )
