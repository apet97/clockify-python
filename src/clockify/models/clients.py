"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import Currency


class Client(ClockifyResponseModel):
    address: str | None = None
    archived: bool
    cc_emails: list[str] | None = Field(default=None, alias="ccEmails")
    currency_code: Currency | None = Field(default=None, alias="currencyCode")
    currency_id: str | None = Field(default=None, alias="currencyId")
    email: str | None = None
    id: str
    name: str
    note: str | None = None
    workspace_id: str = Field(alias="workspaceId")


class ClientCreate(ClockifyRequestModel):
    address: str | None = None
    email: str | None = None
    name: str
    note: str | None = None


class ClientUpdate(ClockifyRequestModel):
    address: str | None = None
    email: str | None = None
    name: str
    note: str | None = None
    archived: bool | None = None
    cc_emails: list[str] | None = Field(default=None, alias="ccEmails")
    currency_id: str | None = Field(default=None, alias="currencyId")
