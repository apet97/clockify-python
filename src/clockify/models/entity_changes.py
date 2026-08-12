"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyResponseModel

# Entity-change document type accepted by Clockify. Values are plural except TIME_ENTRY and USER.
ChangeTrackerDocumentType = Literal[
    "APPROVAL_REQUESTS",
    "BALANCE",
    "CLIENTS",
    "CUSTOM_FIELDS",
    "HOLIDAYS",
    "INVOICES",
    "PROJECTS",
    "PTO_POLICY",
    "SCHEDULED_ASSIGNMENT",
    "TAGS",
    "TASKS",
    "TIME_ENTRY",
    "TIME_ENTRY_CUSTOM_FIELD_VALUE",
    "TIME_ENTRY_RATE",
    "TIME_OFF_REQUEST",
    "USER",
    "USER_GROUPS",
]


class EntityChangeDocumentAuditMetadata(ClockifyResponseModel):
    """Creation and last-update instants for the record."""

    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class EntityChangeDocument(ClockifyResponseModel):
    """One entity-change record. Carries audit timestamps and the document type alongside the changed entity's own fields, which vary by `type`."""

    audit_metadata: EntityChangeDocumentAuditMetadata | None = Field(
        default=None, alias="auditMetadata"
    )
    document_code: ChangeTrackerDocumentType | None = Field(default=None, alias="documentCode")
    id: str | None = None
