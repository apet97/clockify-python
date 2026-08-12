"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from clockify.models.base import ClockifyResponseModel


class SharedAttendanceFilterUsers(ClockifyResponseModel):
    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["ALL", "ACTIVE", "INACTIVE"] | None = None


class SharedAttendanceFilter(ClockifyResponseModel):
    """VERIFIED: only `attendanceFilter` accepted on attendance endpoint."""

    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    users: SharedAttendanceFilterUsers | None = None


class SharedDetailedFilter(ClockifyResponseModel):
    """VERIFIED: only `detailedFilter` accepted on detailed endpoint."""

    audit_filter: dict[str, Any] | None = Field(default=None, alias="auditFilter")
    options: dict[str, Any] | None = None
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    sort_column: str | None = Field(default=None, alias="sortColumn")
    sort_order: Literal["ASCENDING", "DESCENDING"] | None = Field(default=None, alias="sortOrder")


class SharedReport(ClockifyResponseModel):
    filter: SharedReportFilter | None = None
    fixed_date: bool | None = Field(default=None, alias="fixedDate")
    id: str | None = None
    is_public: bool | None = Field(default=None, alias="isPublic")
    link: str | None = None
    name: str | None = None
    report_author: str | None = Field(default=None, alias="reportAuthor")
    type: (
        Literal[
            "SUMMARY",
            "DETAILED",
            "WEEKLY",
            "EXPENSE_DETAILED",
            "INVOICE_TIME",
            "KIOSK_PIN_LIST",
            "ATTENDANCE_DETAILED",
            "ATTENDANCE_SUMMARY",
            "ASSIGNMENT_LIST",
            "ASSIGNMENT_SCHEDULE",
            "APPROVAL_DETAILED",
            "APPROVAL_SUMMARY",
            "BALANCE_LIST",
            "INVOICE_AMOUNT_LIST",
            "INVOICE_DETAILED",
            "TIMEOFF_DETAILED",
            "TIMEOFF_HOLIDAY",
            "TIMEOFF_BALANCE",
            "EXPENSE_SUMMARY",
        ]
        | None
    ) = None
    user_id: str | None = Field(default=None, alias="userId")
    visible_to_user_groups: list[dict[str, Any]] | None = Field(
        default=None, alias="visibleToUserGroups"
    )
    visible_to_users: list[dict[str, Any]] | None = Field(default=None, alias="visibleToUsers")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class SharedReportCreate(ClockifyResponseModel):
    """Body keys: `type` (NOT reportType) and `filter` (NOT filters, singular). Required nested fields: filter.exportType, filter.dateRangeStart, filter.dateRangeEnd."""

    filter: SharedReportFilter
    is_public: bool | None = Field(default=None, alias="isPublic")
    name: str
    type: Literal[
        "SUMMARY",
        "DETAILED",
        "WEEKLY",
        "EXPENSE_DETAILED",
        "INVOICE_TIME",
        "KIOSK_PIN_LIST",
        "ATTENDANCE_DETAILED",
        "ATTENDANCE_SUMMARY",
        "ASSIGNMENT_LIST",
        "ASSIGNMENT_SCHEDULE",
        "APPROVAL_DETAILED",
        "APPROVAL_SUMMARY",
        "BALANCE_LIST",
        "INVOICE_AMOUNT_LIST",
        "INVOICE_DETAILED",
        "TIMEOFF_DETAILED",
        "TIMEOFF_HOLIDAY",
        "TIMEOFF_BALANCE",
        "EXPENSE_SUMMARY",
    ]


class SharedReportDataGroupTotals(ClockifyResponseModel):
    group_one_total_count: int | None = Field(default=None, alias="groupOneTotalCount")


class SharedReportData(ClockifyResponseModel):
    """Rendered payload of a shared report. `groupOne` and `donutChart` rows follow the saved report's grouping, so their properties vary; the keys listed here are the ones observed for a SUMMARY report grouped by project."""

    donut_chart: list[dict[str, Any]] | None = Field(default=None, alias="donutChart")
    filters: dict[str, Any] | None = None
    group_one: list[SharedReportGroupRow] | None = Field(default=None, alias="groupOne")
    group_totals: SharedReportDataGroupTotals | None = Field(default=None, alias="groupTotals")
    totals: list[SharedReportTotals] | None = None


class SharedReportFilter(ClockifyResponseModel):
    attendance_filter: SharedAttendanceFilter | None = Field(default=None, alias="attendanceFilter")
    date_range_end: str = Field(alias="dateRangeEnd")
    date_range_start: str = Field(alias="dateRangeStart")
    detailed_filter: SharedDetailedFilter | None = Field(default=None, alias="detailedFilter")
    export_type: Literal["JSON_V1", "JSON", "CSV", "XLSX", "PDF"] = Field(alias="exportType")
    summary_filter: SharedSummaryFilter | None = Field(default=None, alias="summaryFilter")
    weekly_filter: SharedWeeklyFilter | None = Field(default=None, alias="weeklyFilter")


class SharedReportGroupRow(ClockifyResponseModel):
    _id: str | None = None
    amount: float | None = None
    amounts: list[dict[str, Any]] | None = None
    client_name: str | None = Field(default=None, alias="clientName")
    color: str | None = None
    currency: str | None = None
    duration: int | None = None
    name: str | None = None
    name_lower_case: str | None = Field(default=None, alias="nameLowerCase")
    workspace_currency_code: str | None = Field(default=None, alias="workspaceCurrencyCode")


class SharedReportListEnvelope(ClockifyResponseModel):
    count: int | None = None
    reports: list[SharedReport] | None = None


class SharedReportTotals(ClockifyResponseModel):
    _id: str | None = None
    amounts: list[dict[str, Any]] | None = None
    entries_count: int | None = Field(default=None, alias="entriesCount")
    num_of_currencies: int | None = Field(default=None, alias="numOfCurrencies")
    total_amount: float | None = Field(default=None, alias="totalAmount")
    total_amount_by_currency: list[dict[str, Any]] | None = Field(
        default=None, alias="totalAmountByCurrency"
    )
    total_billable_time: int | None = Field(default=None, alias="totalBillableTime")
    total_time: int | None = Field(default=None, alias="totalTime")


class SharedSummaryFilter(ClockifyResponseModel):
    """VERIFIED: only `summaryFilter` is accepted on the summary endpoint (NOT `detailedFilter`/`weeklyFilter`/`attendanceFilter`)."""

    groups: list[
        Literal["CLIENT", "PROJECT", "TASK", "DATE", "WEEK", "MONTH", "TIMEENTRY", "USER", "TAG"]
    ]
    sort_column: str | None = Field(default=None, alias="sortColumn")


class SharedWeeklyFilter(ClockifyResponseModel):
    """VERIFIED: only `weeklyFilter` accepted on weekly endpoint. Date range MUST be exactly 7 days or upstream returns `{code:501, message:"Please select date range of exactly 7 days for weekly report"}`."""

    group: Literal["PROJECT", "USER"]
    subgroup: Literal["TIME"]
