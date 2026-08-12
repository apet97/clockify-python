"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class ApprovalDateRangeDto(ClockifyResponseModel):
    end: str | None = None
    start: str | None = None


class BalanceAssignmentV1Dto(ClockifyResponseModel):
    accrued: float | None = None
    balance: float | None = None
    date_range: ApprovalDateRangeDto | None = Field(default=None, alias="dateRange")
    id: str | None = None
    policy_id: str | None = Field(default=None, alias="policyId")
    user_id: str | None = Field(default=None, alias="userId")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class CreateBalanceAssignmentV1Request(ClockifyRequestModel):
    balance: float
    date_range: DateRangeV1Request | None = Field(default=None, alias="dateRange")
    note: str | None = None
    policy_id: str = Field(alias="policyId")
    user_ids: list[str] = Field(alias="userIds")


class DateRangeV1Request(ClockifyRequestModel):
    """Represents the date range when the new balance will be usable. If null, this will default to the current day until the same day next year."""

    end: str | None = None
    start: str | None = None


class DeleteBalanceAssignmentV1Request(ClockifyRequestModel):
    note: str


class UpdateBalanceAssignmentV1Request(ClockifyRequestModel):
    balance_change: float = Field(alias="balanceChange")
    date_range: DateRangeV1Request | None = Field(default=None, alias="dateRange")
    note: str | None = None
