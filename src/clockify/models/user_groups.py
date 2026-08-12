"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class AddUserToGroupRequest(ClockifyRequestModel):
    """Request body for adding a user to a group."""

    user_id: str = Field(alias="userId")


class UserGroupDtoV1(ClockifyResponseModel):
    """Represents a user group."""

    id: str | None = None
    name: str | None = None
    team_managers: list[UserRedactedDtoV1] | None = Field(default=None, alias="teamManagers")
    user_ids: list[str] | None = Field(default=None, alias="userIds")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class UserGroupRequest(ClockifyRequestModel):
    """Request body for creating or updating a user group."""

    name: str


# Column to be used as the sorting criteria.
UserGroupSortColumn = Literal["ID", "NAME"]

# Sorting mode.
UserGroupsSortOrder = Literal["ASCENDING", "DESCENDING"]


class UserRedactedDtoV1(ClockifyResponseModel):
    """Represents a redacted user object."""

    id: str | None = None
    name: str | None = None
