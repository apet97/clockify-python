"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel

AuditLogAction = Literal[
    "CREATE_TIME_PERSONAL_TIMER",
    "CREATE_TIME_PERSONAL_MANUAL",
    "CREATE_TIME_IMPORT",
    "CREATE_TIME_KIOSK",
    "CREATE_TIME_FOR_OTHER",
    "RESTORE_TIME",
    "RESTORE_TIME_FOR_OTHER",
    "UPDATE_TIME_PERSONAL",
    "UPDATE_TIME_FOR_OTHER",
    "DELETE_TIME_PERSONAL",
    "DELETE_TIME_FOR_OTHER",
    "CREATE_PROJECT",
    "CREATE_PROJECT_IMPORT",
    "CREATE_PROJECT_QUICKBOOKS",
    "UPDATE_PROJECT",
    "DELETE_PROJECT",
    "CREATE_TASK",
    "CREATE_TASK_IMPORT",
    "UPDATE_TASK",
    "DELETE_TASK",
    "CREATE_CLIENT",
    "CREATE_CLIENT_IMPORT",
    "CREATE_CLIENT_QUICKBOOKS",
    "UPDATE_CLIENT",
    "DELETE_CLIENT",
    "CREATE_TAG",
    "CREATE_TAG_IMPORT",
    "UPDATE_TAG",
    "DELETE_TAG",
    "CREATE_EXPENSE",
    "CREATE_EXPENSE_FOR_OTHER",
    "RESTORE_EXPENSE",
    "RESTORE_EXPENSE_FOR_OTHER",
    "UPDATE_EXPENSE",
    "UPDATE_EXPENSE_FOR_OTHER",
    "DELETE_EXPENSE",
    "DELETE_EXPENSE_FOR_OTHER",
]


class AuditLogAuthorsFilter(ClockifyRequestModel):
    """Author filter. Include SYSTEM to retrieve system audit logs."""

    author_ids: list[str] | None = Field(default=None, alias="authorIds")
    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN"] | None = None


class AuditLogEntry(ClockifyResponseModel):
    """Minimal audit log entry shape observed from the audit-log service."""

    action: str | None = None
    content: str | None = None
    previous_content: str | None = Field(default=None, alias="previousContent")
    timestamp: str | None = None
    user_email: str | None = Field(default=None, alias="userEmail")
    user_id: str | None = Field(default=None, alias="userId")
    user_name: str | None = Field(default=None, alias="userName")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class AuditLogRequest(ClockifyRequestModel):
    """Request body accepted by the dedicated audit-log service."""

    actions: list[AuditLogAction]
    authors: AuditLogAuthorsFilter
    end: str
    page: int | None = None
    page_size: int | None = Field(default=None, alias="page-size")
    start: str


AuditLogResponse = list[AuditLogEntry]
