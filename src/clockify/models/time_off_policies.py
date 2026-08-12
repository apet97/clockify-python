"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import AutomaticTimeEntryCreationRequest


class AutomaticAccrualDto(ClockifyResponseModel):
    """Represents automatic accrual settings."""

    amount: float | None = None
    period: Literal["MONTH", "YEAR"] | None = None
    time_unit: Literal["DAYS", "HOURS"] | None = Field(default=None, alias="timeUnit")


class AutomaticAccrualRequest(ClockifyRequestModel):
    """Provide automatic accrual settings."""

    amount: float
    period: Literal["MONTH", "YEAR"] | None = None
    time_unit: Literal["DAYS", "HOURS"] | None = Field(default=None, alias="timeUnit")


class CreateTimeOffPolicyRequest(ClockifyRequestModel):
    """Request body for creating a time off policy."""

    allow_half_day: bool | None = Field(default=None, alias="allowHalfDay")
    allow_negative_balance: bool | None = Field(default=None, alias="allowNegativeBalance")
    approve: PolicyApprovalDto
    archived: bool | None = None
    automatic_accrual: AutomaticAccrualRequest | None = Field(
        default=None, alias="automaticAccrual"
    )
    automatic_time_entry_creation: AutomaticTimeEntryCreationRequest | None = Field(
        default=None, alias="automaticTimeEntryCreation"
    )
    color: str | None = None
    everyone_including_new: bool | None = Field(default=None, alias="everyoneIncludingNew")
    has_expiration: bool | None = Field(default=None, alias="hasExpiration")
    icon: (
        Literal[
            "UMBRELLA",
            "SNOWFLAKE",
            "FAMILY",
            "PLANE",
            "STETHOSCOPE",
            "HEALTH_METRICS",
            "CHILDCARE",
            "LUGGAGE",
            "MONETIZATION",
            "CALENDAR",
        ]
        | None
    ) = None
    name: str
    negative_balance: NegativeBalanceRequest | None = Field(default=None, alias="negativeBalance")
    time_unit: Literal["DAYS", "HOURS"] | None = Field(default=None, alias="timeUnit")
    user_groups: PoliciesUserGroupIdsSchema | None = Field(default=None, alias="userGroups")
    users: PoliciesUserIdsSchema | None = None


class NegativeBalanceDto(ClockifyResponseModel):
    """Represents negative balance data including amount, time unit, and period."""

    amount: float | None = None
    period: str | None = None
    should_reset: bool | None = Field(default=None, alias="shouldReset")
    time_unit: str | None = Field(default=None, alias="timeUnit")


class NegativeBalanceRequest(ClockifyRequestModel):
    """Negative balance data to use for creating or updating the policy."""

    amount: float | None = None
    amount_valid_for_time_unit: bool | None = Field(default=None, alias="amountValidForTimeUnit")
    period: Literal["MONTH", "YEAR"] | None = None
    should_reset: bool | None = Field(default=None, alias="shouldReset")
    time_unit: Literal["DAYS", "HOURS"] | None = Field(default=None, alias="timeUnit")


class PoliciesAutomaticTimeEntryCreationDto(ClockifyResponseModel):
    """Represents automatic time entry creation settings."""

    default_entities: PoliciesDefaultEntitiesDto | None = Field(
        default=None, alias="defaultEntities"
    )
    enabled: bool | None = None


class PoliciesDefaultEntitiesDto(ClockifyResponseModel):
    """Default project and task for automatically created time entries."""

    project_id: str | None = Field(default=None, alias="projectId")
    task_id: str | None = Field(default=None, alias="taskId")


class PoliciesUserGroupIdsSchema(ClockifyRequestModel):
    """User group filter with identifiers and status."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN"] | None = None
    ids: list[str] | None = None
    status: Literal["ALL", "ACTIVE", "INACTIVE"] | None = None


class PoliciesUserIdsSchema(ClockifyRequestModel):
    """User filter with identifiers and status."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN"] | None = None
    ids: list[str] | None = None
    status: Literal["ALL", "ACTIVE", "INACTIVE"] | None = None


class Policy(ClockifyResponseModel):
    """Represents a time off policy."""

    allow_half_day: bool | None = Field(default=None, alias="allowHalfDay")
    allow_negative_balance: bool | None = Field(default=None, alias="allowNegativeBalance")
    approve: PolicyApprovalDto | None = None
    archived: bool | None = None
    automatic_accrual: AutomaticAccrualDto | None = Field(default=None, alias="automaticAccrual")
    automatic_time_entry_creation: PoliciesAutomaticTimeEntryCreationDto | None = Field(
        default=None, alias="automaticTimeEntryCreation"
    )
    color: str | None = None
    everyone_including_new: bool | None = Field(default=None, alias="everyoneIncludingNew")
    icon: (
        Literal[
            "UMBRELLA",
            "SNOWFLAKE",
            "FAMILY",
            "PLANE",
            "STETHOSCOPE",
            "HEALTH_METRICS",
            "CHILDCARE",
            "LUGGAGE",
            "MONETIZATION",
            "CALENDAR",
        ]
        | None
    ) = None
    id: str | None = None
    name: str | None = None
    negative_balance: NegativeBalanceDto | None = Field(default=None, alias="negativeBalance")
    project_id: str | None = Field(default=None, alias="projectId")
    time_unit: Literal["DAYS", "HOURS"] | None = Field(default=None, alias="timeUnit")
    user_group_ids: list[str] | None = Field(default=None, alias="userGroupIds")
    user_ids: list[str] | None = Field(default=None, alias="userIds")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class PolicyApprovalDto(ClockifyResponseModel):
    """Represents policy approval settings."""

    requires_approval: bool | None = Field(default=None, alias="requiresApproval")
    specific_members: bool | None = Field(default=None, alias="specificMembers")
    team_managers: bool | None = Field(default=None, alias="teamManagers")
    user_ids: list[str] | None = Field(default=None, alias="userIds")


class PolicyStatusChangeRequest(ClockifyRequestModel):
    """Request body for changing a policy status."""

    status: Literal["ACTIVE", "ARCHIVED"]


class UpdateTimeOffPolicyRequest(ClockifyRequestModel):
    """Request body for updating a time off policy."""

    allow_half_day: bool = Field(alias="allowHalfDay")
    allow_negative_balance: bool = Field(alias="allowNegativeBalance")
    approve: PolicyApprovalDto
    archived: bool
    automatic_accrual: AutomaticAccrualRequest | None = Field(
        default=None, alias="automaticAccrual"
    )
    automatic_time_entry_creation: AutomaticTimeEntryCreationRequest | None = Field(
        default=None, alias="automaticTimeEntryCreation"
    )
    color: str | None = None
    everyone_including_new: bool = Field(alias="everyoneIncludingNew")
    has_expiration: bool = Field(alias="hasExpiration")
    icon: (
        Literal[
            "UMBRELLA",
            "SNOWFLAKE",
            "FAMILY",
            "PLANE",
            "STETHOSCOPE",
            "HEALTH_METRICS",
            "CHILDCARE",
            "LUGGAGE",
            "MONETIZATION",
            "CALENDAR",
        ]
        | None
    ) = None
    name: str
    negative_balance: NegativeBalanceRequest | None = Field(default=None, alias="negativeBalance")
    user_groups: PoliciesUserGroupIdsSchema = Field(alias="userGroups")
    users: PoliciesUserIdsSchema
