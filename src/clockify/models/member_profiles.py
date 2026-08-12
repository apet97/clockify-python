"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import (
    UpsertUserCustomFieldRequest,
    UsersCustomFieldType,
    UsersDayOfWeek,
)


class CustomFieldDefaultValuesDtoV1(ClockifyResponseModel):
    """Represents a custom field default values object."""

    project_id: str | None = Field(default=None, alias="projectId")
    status: str | None = None
    value: Any | None = None


class CustomFieldDtoV1(ClockifyResponseModel):
    """Represents a custom field."""

    allowed_values: list[str] | None = Field(default=None, alias="allowedValues")
    description: str | None = None
    entity_type: str | None = Field(default=None, alias="entityType")
    id: str | None = None
    name: str | None = None
    only_admin_can_edit: bool | None = Field(default=None, alias="onlyAdminCanEdit")
    placeholder: str | None = None
    project_default_values: list[CustomFieldDefaultValuesDtoV1] | None = Field(
        default=None, alias="projectDefaultValues"
    )
    required: bool | None = None
    status: str | None = None
    type: UsersCustomFieldType | None = None
    workspace_default_value: Any | None = Field(default=None, alias="workspaceDefaultValue")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class MemberProfileDtoV1(ClockifyResponseModel):
    """Represents a member profile."""

    email: str | None = None
    has_password: bool | None = Field(default=None, alias="hasPassword")
    has_pending_approval_request: bool | None = Field(
        default=None, alias="hasPendingApprovalRequest"
    )
    image_url: str | None = Field(default=None, alias="imageUrl")
    name: str | None = None
    user_custom_field_values: list[UserCustomFieldValueFullDtoV1] | None = Field(
        default=None, alias="userCustomFieldValues"
    )
    week_start: UsersDayOfWeek | None = Field(default=None, alias="weekStart")
    work_capacity: str | None = Field(default=None, alias="workCapacity")
    working_days: (
        list[Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]]
        | None
    ) = Field(default=None, alias="workingDays")
    workspace_number: int | None = Field(default=None, alias="workspaceNumber")


class MemberProfileUpdateRequest(ClockifyRequestModel):
    """Request body for updating a member profile."""

    image_url: str | None = Field(default=None, alias="imageUrl")
    name: str | None = None
    remove_profile_image: bool | None = Field(default=None, alias="removeProfileImage")
    user_custom_fields: list[UpsertUserCustomFieldRequest] | None = Field(
        default=None, alias="userCustomFields"
    )
    week_start: UsersDayOfWeek | None = Field(default=None, alias="weekStart")
    work_capacity: str | None = Field(default=None, alias="workCapacity")
    working_days: (
        list[Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]]
        | None
    ) = Field(default=None, alias="workingDays")


class UserCustomFieldValueFullDtoV1(ClockifyResponseModel):
    """Represents a full user custom field value object."""

    custom_field: CustomFieldDtoV1 | None = Field(default=None, alias="customField")
    custom_field_id: str | None = Field(default=None, alias="customFieldId")
    name: str | None = None
    source_type: Literal["WORKSPACE", "USER"] | None = Field(default=None, alias="sourceType")
    type: UsersCustomFieldType | None = None
    user_id: str | None = Field(default=None, alias="userId")
    value: Any | None = None
