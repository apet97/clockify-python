"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import AutomaticTimeEntryCreationRequest


class AutomaticTimeEntryCreationDto(ClockifyResponseModel):
    """Represents automatic time entry creation settings."""

    default_entities: DefaultEntitiesDto | None = Field(default=None, alias="defaultEntities")
    enabled: bool | None = None


class ContainsUserGroupFilterRequest(ClockifyRequestModel):
    """Provide list with user group ids and corresponding status."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"] | None = None


class ContainsUsersFilterRequestForHoliday(ClockifyRequestModel):
    """Provide list with user ids and corresponding status."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["ALL", "ACTIVE", "INACTIVE"] | None = None
    statuses: list[str] | None = None


class CreateHolidayRequest(ClockifyRequestModel):
    automatic_time_entry_creation: AutomaticTimeEntryCreationRequest | None = Field(
        default=None, alias="automaticTimeEntryCreation"
    )
    color: str | None = None
    date_period: DatePeriodRequest = Field(alias="datePeriod")
    everyone_including_new: bool | None = Field(default=None, alias="everyoneIncludingNew")
    name: str
    occurs_annually: bool | None = Field(default=None, alias="occursAnnually")
    user_groups: UserGroupIdsSchema | None = Field(default=None, alias="userGroups")
    users: UserIdsSchema | None = None


class DatePeriod(ClockifyResponseModel):
    """Represents startDate and endDate of the holiday. Date is in format yyyy-mm-dd."""

    end_date: str | None = Field(default=None, alias="endDate")
    start_date: str | None = Field(default=None, alias="startDate")


class DatePeriodRequest(ClockifyRequestModel):
    """Provide startDate and endDate for the holiday."""

    end_date: str = Field(alias="endDate")
    start_date: str = Field(alias="startDate")


class DefaultEntitiesDto(ClockifyResponseModel):
    project_id: str | None = Field(default=None, alias="projectId")
    task_id: str | None = Field(default=None, alias="taskId")


class EntityIdNameDto(ClockifyResponseModel):
    id: str | None = None
    name: str | None = None


class HolidayDetailsDto(ClockifyResponseModel):
    """Represents a holiday with detailed user and user group assignments."""

    automatic_time_entry_creation: AutomaticTimeEntryCreationDto | None = Field(
        default=None, alias="automaticTimeEntryCreation"
    )
    color: str | None = None
    date_period: DatePeriod | None = Field(default=None, alias="datePeriod")
    everyone_including_new: bool | None = Field(default=None, alias="everyoneIncludingNew")
    id: str | None = None
    name: str | None = None
    occurs_annually: bool | None = Field(default=None, alias="occursAnnually")
    user_group_ids: list[str] | None = Field(default=None, alias="userGroupIds")
    user_groups: list[EntityIdNameDto] | None = Field(default=None, alias="userGroups")
    user_ids: list[str] | None = Field(default=None, alias="userIds")
    users: list[EntityIdNameDto] | None = None
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class HolidayDto(ClockifyResponseModel):
    """Represents a holiday on a workspace."""

    automatic_time_entry_creation: bool | None = Field(
        default=None, alias="automaticTimeEntryCreation"
    )
    date_period: DatePeriod | None = Field(default=None, alias="datePeriod")
    everyone_including_new: bool | None = Field(default=None, alias="everyoneIncludingNew")
    id: str | None = None
    name: str | None = None
    occurs_annually: bool | None = Field(default=None, alias="occursAnnually")
    project_id: str | None = Field(default=None, alias="projectId")
    task_id: str | None = Field(default=None, alias="taskId")
    user_group_ids: list[str] | None = Field(default=None, alias="userGroupIds")
    user_ids: list[str] | None = Field(default=None, alias="userIds")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class UpdateHolidayRequest(ClockifyRequestModel):
    automatic_time_entry_creation: AutomaticTimeEntryCreationRequest | None = Field(
        default=None, alias="automaticTimeEntryCreation"
    )
    color: str | None = None
    date_period: DatePeriodRequest = Field(alias="datePeriod")
    everyone_including_new: bool | None = Field(default=None, alias="everyoneIncludingNew")
    name: str
    occurs_annually: bool = Field(alias="occursAnnually")
    user_groups: ContainsUserGroupFilterRequest | None = Field(default=None, alias="userGroups")
    users: ContainsUsersFilterRequestForHoliday | None = None


class UserGroupIdsSchema(ClockifyRequestModel):
    """Provide list with user group ids and corresponding status."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN"] | None = None
    ids: list[str] | None = None
    status: Literal["ALL", "ACTIVE", "INACTIVE"] | None = None


class UserIdsSchema(ClockifyRequestModel):
    """Provide list with user ids and corresponding status."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN"] | None = None
    ids: list[str] | None = None
    status: Literal["ALL", "ACTIVE", "INACTIVE"] | None = None
