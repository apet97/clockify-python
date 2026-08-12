"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class CreateCustomFieldRequest(ClockifyRequestModel):
    allowed_values: list[str] | None = Field(default=None, alias="allowedValues")
    description: str | None = None
    entity_type: CustomFieldEntityType | None = Field(default=None, alias="entityType")
    name: str
    only_admin_can_edit: bool | None = Field(default=None, alias="onlyAdminCanEdit")
    placeholder: str | None = None
    required: bool | None = None
    status: CustomFieldStatus | None = None
    type: CustomFieldType
    workspace_default_value: CustomFieldValue | None = Field(
        default=None, alias="workspaceDefaultValue"
    )


class CustomField(ClockifyResponseModel):
    """Custom field data transfer object."""

    allowed_values: list[str] | None = Field(default=None, alias="allowedValues")
    description: str | None = None
    entity_type: CustomFieldEntityType | None = Field(default=None, alias="entityType")
    id: str | None = None
    name: str | None = None
    only_admin_can_edit: bool | None = Field(default=None, alias="onlyAdminCanEdit")
    placeholder: str | None = None
    project_default_values: list[CustomFieldDefaultValue] | None = Field(
        default=None, alias="projectDefaultValues"
    )
    required: bool | None = None
    status: CustomFieldStatus | None = None
    type: CustomFieldType | None = None
    workspace_default_value: CustomFieldValue | None = Field(
        default=None, alias="workspaceDefaultValue"
    )
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class CustomFieldDefaultValue(ClockifyResponseModel):
    """Custom field default value for a project."""

    project_id: str | None = Field(default=None, alias="projectId")
    status: CustomFieldStatus | None = None
    value: CustomFieldValue | None = None


# Custom field entity type.
CustomFieldEntityType = Literal["TIMEENTRY", "USER"]

# Custom field status.
CustomFieldStatus = Literal["INACTIVE", "VISIBLE", "INVISIBLE"]

# Custom field type.
CustomFieldType = Literal[
    "TXT", "NUMBER", "DROPDOWN_SINGLE", "DROPDOWN_MULTIPLE", "CHECKBOX", "LINK"
]

CustomFieldValue = str | float | bool | list[str] | dict[str, Any] | None


class Error(ClockifyResponseModel):
    """Generic error response."""


class UpdateCustomFieldRequest(ClockifyRequestModel):
    allowed_values: list[str] | None = Field(default=None, alias="allowedValues")
    description: str | None = None
    name: str
    only_admin_can_edit: bool | None = Field(default=None, alias="onlyAdminCanEdit")
    placeholder: str | None = None
    required: bool | None = None
    status: CustomFieldStatus | None = None
    type: CustomFieldType
    workspace_default_value: CustomFieldValue | None = Field(
        default=None, alias="workspaceDefaultValue"
    )


class UpdateProjectCustomFieldRequest(ClockifyRequestModel):
    default_value: CustomFieldValue | None = Field(default=None, alias="defaultValue")
    status: CustomFieldStatus | None = None
