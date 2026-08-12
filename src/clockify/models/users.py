"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import (
    RateDto,
    UpsertUserCustomFieldRequest,
    UsersCustomFieldType,
    UsersDayOfWeek,
)

# Represents account status enum.
AccountStatus = Literal[
    "ACTIVE",
    "PENDING_EMAIL_VERIFICATION",
    "DELETED",
    "NOT_REGISTERED",
    "LIMITED",
    "LIMITED_DELETED",
]


class AddLimitedUsersRequest(ClockifyRequestModel):
    users: list[LimitedUserRequest]


class AddUserToWorkspaceRequest(ClockifyRequestModel):
    email: str


class HourlyRateDtoV1(ClockifyResponseModel):
    """Represents an hourly rate object."""

    amount: int | None = None
    currency: str | None = None


class LimitedUserRequest(ClockifyRequestModel):
    cost_rate: int | None = Field(default=None, alias="costRate")
    hourly_rate: int | None = Field(default=None, alias="hourlyRate")
    name: str
    user_custom_fields: list[UpsertUserCustomFieldRequest] | None = Field(
        default=None, alias="userCustomFields"
    )
    user_groups: list[str] | None = Field(default=None, alias="userGroups")
    week_start: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="weekStart")
    work_capacity: str | None = Field(default=None, alias="workCapacity")
    working_days: (
        list[Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]]
        | None
    ) = Field(default=None, alias="workingDays")


class ManagerRoleRequest(ClockifyRequestModel):
    """Request body used to add or remove a user's manager role."""

    entity_id: str = Field(alias="entityId")
    role: Literal["WORKSPACE_ADMIN", "TEAM_MANAGER", "PROJECT_MANAGER"]
    source_type: Literal["USER_GROUP"] | None = Field(default=None, alias="sourceType")


class RoleAssignmentDtoV1(ClockifyResponseModel):
    role: str | None = None
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class SummaryReportSettingsDtoV1(ClockifyResponseModel):
    """Represents a summary report settings object."""

    group: str
    subgroup: str


class UpdateUserCustomFieldValueRequest(ClockifyRequestModel):
    value: Any | None


class UpdateUserHourlyRateRequest(ClockifyRequestModel):
    amount: int
    since: str | None = None


class UpdateUserStatusRequest(ClockifyRequestModel):
    status: Literal["ACTIVE", "INACTIVE"]


class UserCustomFieldValueDtoV1(ClockifyResponseModel):
    """Represents a user custom field value object."""

    custom_field_id: str | None = Field(default=None, alias="customFieldId")
    custom_field_name: str | None = Field(default=None, alias="customFieldName")
    custom_field_type: UsersCustomFieldType | None = Field(default=None, alias="customFieldType")
    user_id: str | None = Field(default=None, alias="userId")
    value: Any | None = None


class UserDtoV1(ClockifyResponseModel):
    """Represents a user."""

    active_workspace: str | None = Field(default=None, alias="activeWorkspace")
    custom_fields: list[UserCustomFieldValueDtoV1] | None = Field(
        default=None, alias="customFields"
    )
    default_workspace: str | None = Field(default=None, alias="defaultWorkspace")
    email: str
    id: str
    memberships: list[UsersMembershipDtoV1] | None = None
    name: str
    profile_picture: str | None = Field(default=None, alias="profilePicture")
    settings: UserSettingsDtoV1 | None = None
    status: AccountStatus
    roles: list[dict[str, Any]] | None = None


class UserFilterRequest(ClockifyRequestModel):
    """Request body for filtering workspace users."""

    account_statuses: list[AccountStatus] | None = Field(default=None, alias="accountStatuses")
    email: str | None = None
    include_roles: bool | None = Field(default=None, alias="includeRoles")
    memberships: Literal["ALL", "NONE", "WORKSPACE", "PROJECT", "USERGROUP"] | None = None
    name: str | None = None
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    project_id: str | None = Field(default=None, alias="projectId")
    roles: list[Literal["WORKSPACE_ADMIN", "OWNER", "TEAM_MANAGER", "PROJECT_MANAGER"]] | None = (
        None
    )
    sort_column: (
        Literal["ID", "EMAIL", "NAME", "NAME_LOWERCASE", "ACCESS", "HOURLYRATE", "COSTRATE"] | None
    ) = Field(default=None, alias="sortColumn")
    sort_order: Literal["ASCENDING", "DESCENDING"] | None = Field(default=None, alias="sortOrder")
    status: Literal["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"] | None = None
    user_groups: list[str] | None = Field(default=None, alias="userGroups")


class UserSettingsDtoV1(ClockifyResponseModel):
    """Represents user settings object."""

    alerts: bool | None = None
    approval: bool | None = None
    collapse_all_project_lists: bool | None = Field(default=None, alias="collapseAllProjectLists")
    dashboard_pin_to_top: bool | None = Field(default=None, alias="dashboardPinToTop")
    dashboard_selection: Literal["ME", "TEAM"] | None = Field(
        default=None, alias="dashboardSelection"
    )
    dashboard_view_type: Literal["PROJECT", "BILLABILITY"] | None = Field(
        default=None, alias="dashboardViewType"
    )
    date_format: str = Field(alias="dateFormat")
    group_similar_entries_disabled: bool | None = Field(
        default=None, alias="groupSimilarEntriesDisabled"
    )
    invoice_reminders: bool | None = Field(default=None, alias="invoiceReminders")
    is_compact_view_on: bool | None = Field(default=None, alias="isCompactViewOn")
    lang: str | None = None
    long_running: bool | None = Field(default=None, alias="longRunning")
    multi_factor_enabled: bool | None = Field(default=None, alias="multiFactorEnabled")
    my_start_of_day: str | None = Field(default=None, alias="myStartOfDay")
    onboarding: bool | None = None
    project_list_collapse: int | None = Field(default=None, alias="projectListCollapse")
    project_picker_task_filter: bool | None = Field(default=None, alias="projectPickerTaskFilter")
    pto: bool | None = None
    reminders: bool | None = None
    scheduled_reports: bool | None = Field(default=None, alias="scheduledReports")
    scheduling: bool | None = None
    send_newsletter: bool | None = Field(default=None, alias="sendNewsletter")
    show_only_working_days: bool | None = Field(default=None, alias="showOnlyWorkingDays")
    summary_report_settings: SummaryReportSettingsDtoV1 | None = Field(
        default=None, alias="summaryReportSettings"
    )
    theme: Literal["DARK", "DEFAULT"] | None = None
    time_format: Literal["HOUR12", "HOUR24"] = Field(alias="timeFormat")
    time_tracking_manual: bool | None = Field(default=None, alias="timeTrackingManual")
    time_zone: str = Field(alias="timeZone")
    week_start: UsersDayOfWeek | None = Field(default=None, alias="weekStart")
    weekly_updates: bool | None = Field(default=None, alias="weeklyUpdates")


class UsersMembershipDtoV1(ClockifyResponseModel):
    """Represents a membership object."""

    cost_rate: RateDto | None = Field(default=None, alias="costRate")
    hourly_rate: HourlyRateDtoV1 | None = Field(default=None, alias="hourlyRate")
    membership_status: Literal["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"] | None = Field(
        default=None, alias="membershipStatus"
    )
    membership_type: Literal["WORKSPACE", "PROJECT", "USERGROUP"] | None = Field(
        default=None, alias="membershipType"
    )
    target_id: str | None = Field(default=None, alias="targetId")
    user_id: str | None = Field(default=None, alias="userId")
