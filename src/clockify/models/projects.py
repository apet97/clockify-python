"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class AssignRemoveUsersRequest(ClockifyRequestModel):
    remove: bool | None = None
    user_groups: ProjectsUserGroupIdsSchema | None = Field(default=None, alias="userGroups")
    user_ids: list[str] | None = Field(default=None, alias="userIds")


class CreateProjectFromTemplateRequest(ClockifyRequestModel):
    client_id: str | None = Field(default=None, alias="clientId")
    color: str | None = None
    is_public: bool | None = Field(default=None, alias="isPublic")
    name: str
    template_project_id: str = Field(alias="templateProjectId")


class CreateProjectRequest(ClockifyRequestModel):
    billable: bool | None = None
    client_id: str | None = Field(default=None, alias="clientId")
    color: str | None = None
    cost_rate: RateRequest | None = Field(default=None, alias="costRate")
    estimate: EstimateRequest | None = None
    hourly_rate: RateRequest | None = Field(default=None, alias="hourlyRate")
    is_public: bool | None = Field(default=None, alias="isPublic")
    memberships: list[MembershipRequest] | None = None
    name: str
    note: str | None = None
    tasks: list[TaskRequest] | None = None


class EstimateDtoV1(ClockifyResponseModel):
    """Represents a project estimate object."""

    estimate: str | None = None
    type: Literal["AUTO", "MANUAL"] | None = None


class EstimateRequest(ClockifyRequestModel):
    """Represents an estimate request object."""

    estimate: str | None = None
    type: Literal["AUTO", "MANUAL"] | None = None


class EstimateResetDto(ClockifyResponseModel):
    """Represents project estimate reset object."""

    day_of_month: int | None = Field(default=None, alias="dayOfMonth")
    day_of_week: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="dayOfWeek")
    hour: int | None = None
    interval: Literal["WEEKLY", "MONTHLY", "YEARLY"] | None = None
    month: (
        Literal[
            "JANUARY",
            "FEBRUARY",
            "MARCH",
            "APRIL",
            "MAY",
            "JUNE",
            "JULY",
            "AUGUST",
            "SEPTEMBER",
            "OCTOBER",
            "NOVEMBER",
            "DECEMBER",
        ]
        | None
    ) = None


class EstimateResetRequest(ClockifyRequestModel):
    """Represents estimate reset request object."""

    active: bool | None = None
    day_of_month: int | None = Field(default=None, alias="dayOfMonth")
    day_of_week: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="dayOfWeek")
    hour: int | None = None
    interval: Literal["WEEKLY", "MONTHLY", "YEARLY"] | None = None
    is_active: bool | None = Field(default=None, alias="isActive")
    month: (
        Literal[
            "JANUARY",
            "FEBRUARY",
            "MARCH",
            "APRIL",
            "MAY",
            "JUNE",
            "JULY",
            "AUGUST",
            "SEPTEMBER",
            "OCTOBER",
            "NOVEMBER",
            "DECEMBER",
        ]
        | None
    ) = None


class EstimateWithOptionsDto(ClockifyResponseModel):
    """Represents a project budget estimate object."""

    active: bool | None = None
    estimate: int | None = None
    include_expenses: bool | None = Field(default=None, alias="includeExpenses")
    reset_option: Literal["WEEKLY", "MONTHLY", "YEARLY"] | None = Field(
        default=None, alias="resetOption"
    )
    type: Literal["AUTO", "MANUAL"] | None = None


class EstimateWithOptionsRequest(ClockifyRequestModel):
    """Represents estimate with options request object."""

    active: bool | None = None
    estimate: int | None = None
    include_expenses: bool | None = Field(default=None, alias="includeExpenses")
    reset_option: Literal["WEEKLY", "MONTHLY", "YEARLY"] | None = Field(
        default=None, alias="resetOption"
    )
    type: Literal["AUTO", "MANUAL"] | None = None


class MembershipDtoV1(ClockifyResponseModel):
    """Represents a membership object."""

    cost_rate: RateDtoV1 | None = Field(default=None, alias="costRate")
    hourly_rate: RateDtoV1 | None = Field(default=None, alias="hourlyRate")
    membership_status: Literal["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"] | None = Field(
        default=None, alias="membershipStatus"
    )
    membership_type: Literal["WORKSPACE", "PROJECT", "USERGROUP"] | None = Field(
        default=None, alias="membershipType"
    )
    target_id: str | None = Field(default=None, alias="targetId")
    user_id: str | None = Field(default=None, alias="userId")


class MembershipRequest(ClockifyRequestModel):
    """Represents a membership request object."""

    hourly_rate: RateRequest | None = Field(default=None, alias="hourlyRate")
    membership_status: Literal["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"] | None = Field(
        default=None, alias="membershipStatus"
    )
    membership_type: Literal["WORKSPACE", "PROJECT", "USERGROUP"] | None = Field(
        default=None, alias="membershipType"
    )
    user_id: str | None = Field(default=None, alias="userId")


class Project(ClockifyResponseModel):
    """Represents a Clockify project."""

    archived: bool
    billable: bool
    budget_estimate: EstimateWithOptionsDto | None = Field(default=None, alias="budgetEstimate")
    client_id: str | None = Field(default=None, alias="clientId")
    client_name: str | None = Field(default=None, alias="clientName")
    color: str
    cost_rate: RateDtoV1 | None = Field(default=None, alias="costRate")
    duration: str | None = None
    estimate: EstimateDtoV1 | None = None
    estimate_reset: EstimateResetDto | None = Field(default=None, alias="estimateReset")
    hourly_rate: RateDtoV1 | None = Field(default=None, alias="hourlyRate")
    id: str
    memberships: list[MembershipDtoV1] | None = None
    name: str
    note: str | None = None
    public: bool
    template: bool
    time_estimate: TimeEstimateDto | None = Field(default=None, alias="timeEstimate")
    workspace_id: str = Field(alias="workspaceId")


class ProjectsUserGroupIdsSchema(ClockifyRequestModel):
    """Provide list with user group ids and corresponding status."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN"] | None = None
    ids: list[str] | None = None
    status: Literal["ALL", "ACTIVE", "INACTIVE"] | None = None


class RateDtoV1(ClockifyResponseModel):
    """Represents an hourly or cost rate object."""

    amount: int | None = None
    currency: str | None = None


class RateRequest(ClockifyRequestModel):
    amount: int
    since: str | None = None


class TaskRequest(ClockifyRequestModel):
    """Represents a task request object used when creating a project."""

    assignee_id: str | None = Field(default=None, alias="assigneeId")
    assignee_ids: list[str] | None = Field(default=None, alias="assigneeIds")
    billable: bool | None = None
    budget_estimate: int | None = Field(default=None, alias="budgetEstimate")
    cost_rate: RateRequest | None = Field(default=None, alias="costRate")
    estimate: str | None = None
    hourly_rate: RateRequest | None = Field(default=None, alias="hourlyRate")
    id: str | None = None
    name: str
    project_id: str | None = Field(default=None, alias="projectId")
    status: Literal["ACTIVE", "DONE", "ALL"] | None = None
    user_group_ids: list[str] | None = Field(default=None, alias="userGroupIds")


class TimeEstimateDto(ClockifyResponseModel):
    """Represents a project time estimate object."""

    active: bool | None = None
    estimate: str | None = None
    include_non_billable: bool | None = Field(default=None, alias="includeNonBillable")
    reset_option: Literal["WEEKLY", "MONTHLY", "YEARLY"] | None = Field(
        default=None, alias="resetOption"
    )
    type: Literal["AUTO", "MANUAL"] | None = None


class TimeEstimateRequest(ClockifyRequestModel):
    """Represents project time estimate request object."""

    active: bool | None = None
    estimate: str | None = None
    include_non_billable: bool | None = Field(default=None, alias="includeNonBillable")
    reset_option: Literal["WEEKLY", "MONTHLY", "YEARLY"] | None = Field(
        default=None, alias="resetOption"
    )
    type: Literal["AUTO", "MANUAL"] | None = None


class UpdateProjectEstimateRequest(ClockifyRequestModel):
    budget_estimate: EstimateWithOptionsRequest | None = Field(default=None, alias="budgetEstimate")
    estimate_reset: EstimateResetRequest | None = Field(default=None, alias="estimateReset")
    time_estimate: TimeEstimateRequest | None = Field(default=None, alias="timeEstimate")


class UpdateProjectMembershipsRequest(ClockifyRequestModel):
    memberships: list[UserIdWithRatesRequest]
    user_groups: ProjectsUserGroupIdsSchema | None = Field(default=None, alias="userGroups")


class UpdateProjectRequest(ClockifyRequestModel):
    archived: bool | None = None
    billable: bool | None = None
    client_id: str | None = Field(default=None, alias="clientId")
    color: str | None = None
    cost_rate: RateRequest | None = Field(default=None, alias="costRate")
    hourly_rate: RateRequest | None = Field(default=None, alias="hourlyRate")
    is_public: bool | None = Field(default=None, alias="isPublic")
    name: str | None = None
    note: str | None = None


class UpdateProjectTemplateRequest(ClockifyRequestModel):
    is_template: bool = Field(alias="isTemplate")


class UserIdWithRatesRequest(ClockifyRequestModel):
    """Represents a user id with cost and hourly rates."""

    cost_rate: RateRequest | None = Field(default=None, alias="costRate")
    hourly_rate: RateRequest | None = Field(default=None, alias="hourlyRate")
    user_id: str = Field(alias="userId")
