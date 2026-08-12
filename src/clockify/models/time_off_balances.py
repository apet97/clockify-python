"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class BalanceDtoV1(ClockifyResponseModel):
    """Balance data transfer object."""

    balance: float | None = None
    id: str | None = None
    negative_balance_amount: float | None = Field(default=None, alias="negativeBalanceAmount")
    negative_balance_limit: bool | None = Field(default=None, alias="negativeBalanceLimit")
    policy_archived: bool | None = Field(default=None, alias="policyArchived")
    policy_id: str | None = Field(default=None, alias="policyId")
    policy_name: str | None = Field(default=None, alias="policyName")
    policy_time_unit: PolicyTimeUnit | None = Field(default=None, alias="policyTimeUnit")
    total: float | None = None
    used: float | None = None
    user_id: str | None = Field(default=None, alias="userId")
    user_name: str | None = Field(default=None, alias="userName")
    workspace_id: str | None = Field(default=None, alias="workspaceId")
    negative_balance_used: float | None = Field(default=None, alias="negativeBalanceUsed")


class BalanceListResponse(ClockifyResponseModel):
    """Paginated balance list response."""

    balances: list[BalanceDtoV1] | None = None
    count: int | None = None


# Valid column for sorting balance results.
BalanceSortColumn = Literal["USER", "POLICY", "USED", "BALANCE", "TOTAL"]

# Sort order.
BalanceSortOrder = Literal["ASCENDING", "DESCENDING"]

# Represents policy time unit.
PolicyTimeUnit = Literal["DAYS", "HOURS"]


class UpdateBalanceRequest(ClockifyRequestModel):
    note: str
    user_ids: list[str] = Field(alias="userIds")
    value: float
