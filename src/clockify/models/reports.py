"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class AmountDto(ClockifyResponseModel):
    type: AmountType | None = None
    value: float | None = None


# Report amount type.
AmountType = Literal["EARNED", "COST", "PROFIT", "HIDE_AMOUNT", "EXPORT"]


class AttendanceDto(ClockifyResponseModel):
    break_: int | None = Field(default=None, alias="break")
    capacity: int | None = None
    date: str | None = None
    end_time: str | None = Field(default=None, alias="endTime")
    has_running_entry: bool | None = Field(default=None, alias="hasRunningEntry")
    image_url: str | None = Field(default=None, alias="imageUrl")
    overtime: int | None = None
    remaining_capacity: int | None = Field(default=None, alias="remainingCapacity")
    start_time: str | None = Field(default=None, alias="startTime")
    time_off: int | None = Field(default=None, alias="timeOff")
    total_duration: int | None = Field(default=None, alias="totalDuration")
    user_id: str | None = Field(default=None, alias="userId")
    user_name: str | None = Field(default=None, alias="userName")


class AttendanceFilter(ClockifyRequestModel):
    """Attendance report filter. This filter is valid only on /reports/attendance."""

    break_filters: list[CompareFilter] | None = Field(default=None, alias="breakFilters")
    capacity_filters: list[CompareFilter] | None = Field(default=None, alias="capacityFilters")
    end_filters: list[CompareFilter] | None = Field(default=None, alias="endFilters")
    has_time_off: bool | None = Field(default=None, alias="hasTimeOff")
    overtime_filters: list[CompareFilter] | None = Field(default=None, alias="overtimeFilters")
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    sort_column: (
        Literal["USER", "DATE", "START", "END", "BREAK", "WORK", "CAPACITY", "OVERTIME", "TIME_OFF"]
        | None
    ) = Field(default=None, alias="sortColumn")
    start_filters: list[CompareFilter] | None = Field(default=None, alias="startFilters")
    work_filters: list[CompareFilter] | None = Field(default=None, alias="workFilters")


class AttendanceReportRequest(ClockifyRequestModel):
    """Request payload for generating attendance reports. Only attendanceFilter is accepted as the report-specific filter."""

    amount_shown: Literal["EARNED", "COST", "PROFIT", "HIDE_AMOUNT", "EXPORT"] | None = Field(
        default=None, alias="amountShown"
    )
    amounts: list[AmountType] | None = None
    approval_state: Literal["APPROVED", "UNAPPROVED", "ALL"] | None = Field(
        default=None, alias="approvalState"
    )
    archived: bool | None = None
    attendance_filter: AttendanceFilter = Field(alias="attendanceFilter")
    billable: bool | None = None
    clients: ContainsArchivedFilter | None = None
    currency: ContainsArchivedFilter | None = None
    custom_fields: list[CustomFieldFilter] | None = Field(default=None, alias="customFields")
    date_format: str | None = Field(default=None, alias="dateFormat")
    date_range_end: str = Field(alias="dateRangeEnd")
    date_range_start: str = Field(alias="dateRangeStart")
    date_range_type: (
        Literal[
            "ABSOLUTE",
            "TODAY",
            "YESTERDAY",
            "THIS_WEEK",
            "LAST_WEEK",
            "PAST_TWO_WEEKS",
            "THIS_MONTH",
            "LAST_MONTH",
            "THIS_YEAR",
            "LAST_YEAR",
        ]
        | None
    ) = Field(default=None, alias="dateRangeType")
    description: str | None = None
    export_type: Literal["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"] | None = Field(
        default=None, alias="exportType"
    )
    invoicing_state: Literal["INVOICED", "UNINVOICED", "ALL"] | None = Field(
        default=None, alias="invoicingState"
    )
    projects: ContainsArchivedFilter | None = None
    rounding: bool | None = None
    sort_order: Literal["ASCENDING", "DESCENDING"] | None = Field(default=None, alias="sortOrder")
    tags: ContainsTagFilter | None = None
    tasks: ContainsTaskFilter | None = None
    time_format: str | None = Field(default=None, alias="timeFormat")
    time_zone: str | None = Field(default=None, alias="timeZone")
    user_groups: ContainsUsersFilter | None = Field(default=None, alias="userGroups")
    user_locale: str | None = Field(default=None, alias="userLocale")
    users: ContainsUsersFilter | None = None
    week_start: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="weekStart")
    without_description: bool | None = Field(default=None, alias="withoutDescription")
    zoom_level: Literal["WEEK", "MONTH", "YEAR"] | None = Field(default=None, alias="zoomLevel")


class AttendanceReportResponse(ClockifyResponseModel):
    """Attendance report response."""

    entities: list[AttendanceDto] | None = None


class AuditFilter(ClockifyRequestModel):
    """Audit filter for detailed reports."""

    duration: int | None = None
    duration_shorter: bool | None = Field(default=None, alias="durationShorter")
    without_project: bool | None = Field(default=None, alias="withoutProject")
    without_task: bool | None = Field(default=None, alias="withoutTask")


class CompareFilter(ClockifyRequestModel):
    """Comparison filter used by attendance filters."""

    filtration_type: Literal["EXACTLY", "LARGER_THAN", "SMALLER_THAN"] = Field(
        alias="filtrationType"
    )
    value: str


class ContainsArchivedFilter(ClockifyRequestModel):
    """Filter by contained archived-aware entities."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["ACTIVE", "ARCHIVED", "ALL"] | None = None


class ContainsArchivedFilterV1(ClockifyRequestModel):
    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["ACTIVE", "ARCHIVED", "ALL"] | None = None


class ContainsTagFilter(ClockifyRequestModel):
    """Filter criteria for tags."""

    contained_in_timeentry: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = Field(
        default=None, alias="containedInTimeentry"
    )
    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["ACTIVE", "ARCHIVED", "ALL"] | None = None


class ContainsTaskFilter(ClockifyRequestModel):
    """Filter criteria for tasks."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["ACTIVE", "ARCHIVED", "ALL"] | None = None


class ContainsTaskFilterV1(ClockifyRequestModel):
    """Represents filter criteria for expenses associated with tasks."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["ACTIVE", "ARCHIVED", "ALL"] | None = None


class ContainsUsersFilter(ClockifyRequestModel):
    """Filter by users or user groups."""

    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["ALL", "ACTIVE_WITH_PENDING", "ACTIVE", "PENDING", "INACTIVE"] | None = None


class ContainsUsersFilterV1(ClockifyRequestModel):
    contains: Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"] | None = None
    ids: list[str] | None = None
    status: Literal["ALL", "ACTIVE_WITH_PENDING", "ACTIVE", "PENDING", "INACTIVE"] | None = None


class CustomFieldFilter(ClockifyRequestModel):
    """Custom field filter."""

    id: str | None = None
    is_empty: bool | None = Field(default=None, alias="isEmpty")
    number_condition: Literal["EQUAL", "GREATER_THAN", "LESS_THAN"] | None = Field(
        default=None, alias="numberCondition"
    )
    type: (
        Literal["TXT", "NUMBER", "DROPDOWN_SINGLE", "DROPDOWN_MULTIPLE", "CHECKBOX", "LINK"] | None
    ) = None
    value: str | float | bool | list[Any] | dict[str, Any] | None = None


class DailyTotalDto(ClockifyResponseModel):
    amount: float | None = None
    date: str | None = None
    duration: float | None = None


class DetailedFilter(ClockifyRequestModel):
    """Detailed report filter. This filter is valid only on /reports/detailed. Pagination belongs in this nested filter as page and pageSize; top-level request page fields are not accepted by /reports/detailed."""

    audit_filter: AuditFilter | None = Field(default=None, alias="auditFilter")
    options: DetailedOptions | None = None
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    sort_column: (
        Literal[
            "ID", "DESCRIPTION", "USER", "DURATION", "DATE", "ZONED_DATE", "NATURAL", "USER_DATE"
        ]
        | None
    ) = Field(default=None, alias="sortColumn")


class DetailedOptions(ClockifyRequestModel):
    """Detailed report options."""

    totals: Literal["CALCULATE", "EXCLUDE"] | None = None


class DetailedReportRequest(ClockifyRequestModel):
    """Request payload for generating detailed time-entry reports. Only detailedFilter is accepted as the report-specific filter."""

    amount_shown: Literal["EARNED", "COST", "PROFIT", "HIDE_AMOUNT", "EXPORT"] | None = Field(
        default=None, alias="amountShown"
    )
    amounts: list[AmountType] | None = None
    approval_state: Literal["APPROVED", "UNAPPROVED", "ALL"] | None = Field(
        default=None, alias="approvalState"
    )
    archived: bool | None = None
    billable: bool | None = None
    clients: ContainsArchivedFilter | None = None
    currency: ContainsArchivedFilter | None = None
    custom_fields: list[CustomFieldFilter] | None = Field(default=None, alias="customFields")
    date_format: str | None = Field(default=None, alias="dateFormat")
    date_range_end: str = Field(alias="dateRangeEnd")
    date_range_start: str = Field(alias="dateRangeStart")
    date_range_type: (
        Literal[
            "ABSOLUTE",
            "TODAY",
            "YESTERDAY",
            "THIS_WEEK",
            "LAST_WEEK",
            "PAST_TWO_WEEKS",
            "THIS_MONTH",
            "LAST_MONTH",
            "THIS_YEAR",
            "LAST_YEAR",
        ]
        | None
    ) = Field(default=None, alias="dateRangeType")
    description: str | None = None
    detailed_filter: DetailedFilter = Field(alias="detailedFilter")
    export_type: Literal["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"] | None = Field(
        default=None, alias="exportType"
    )
    invoicing_state: Literal["INVOICED", "UNINVOICED", "ALL"] | None = Field(
        default=None, alias="invoicingState"
    )
    projects: ContainsArchivedFilter | None = None
    rounding: bool | None = None
    sort_order: Literal["ASCENDING", "DESCENDING"] | None = Field(default=None, alias="sortOrder")
    tags: ContainsTagFilter | None = None
    tasks: ContainsTaskFilter | None = None
    time_format: str | None = Field(default=None, alias="timeFormat")
    time_zone: str | None = Field(default=None, alias="timeZone")
    user_custom_fields: list[CustomFieldFilter] | None = Field(
        default=None, alias="userCustomFields"
    )
    user_groups: ContainsUsersFilter | None = Field(default=None, alias="userGroups")
    user_locale: str | None = Field(default=None, alias="userLocale")
    users: ContainsUsersFilter | None = None
    week_start: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="weekStart")
    without_description: bool | None = Field(default=None, alias="withoutDescription")
    zoom_level: Literal["WEEK", "MONTH", "YEAR"] | None = Field(default=None, alias="zoomLevel")


class DetailedReportResponse(ClockifyResponseModel):
    """Detailed report response. Both timeEntries and timeentries are valid payload keys."""

    time_entries: list[TimeEntryDto] | None = Field(default=None, alias="timeEntries")
    timeentries: list[TimeEntryDto] | None = None
    totals: list[TimeEntryReportTotals] | None = None


class ErrorResponse(ClockifyResponseModel):
    code: str | None = None
    message: str | None = None


class ExpenseDetailedReportDtoV1(ClockifyResponseModel):
    """report"""

    expenses: list[ExpenseReportDtoV1] | None = None
    totals: ExpenseTotalsDtoV1 | None = None


class ExpenseReportDtoV1(ClockifyResponseModel):
    """Represents list of expenses"""

    amount: float | None = None
    approval_request_id: str | None = Field(default=None, alias="approvalRequestId")
    billable: bool | None = None
    category_has_unit_price: bool | None = Field(default=None, alias="categoryHasUnitPrice")
    category_id: str | None = Field(default=None, alias="categoryId")
    category_name: str | None = Field(default=None, alias="categoryName")
    category_unit: str | None = Field(default=None, alias="categoryUnit")
    date: str | None = None
    export_fields: (
        list[
            Literal[
                "PROJECT",
                "CLIENT",
                "TASK",
                "DESCRIPTION",
                "USER",
                "TAGS",
                "START_DATE",
                "START_TIME",
                "END_TIME",
                "DURATION",
                "BILLABLE_AMOUNT",
                "COST_AMOUNT",
                "PROFIT",
                "EMAIL",
                "BILLABLE",
                "BILLABLE_H",
                "NON_BILLABLE_H",
                "END_DATE",
                "DECIMAL_DURATION",
                "BILLABLE_RATE",
                "COST_RATE",
                "APPROVAL",
                "BAR_CHART",
                "PIE_CHART_1",
                "PIE_CHART_2",
                "PIE_CHART_3",
                "RTL",
                "TOTAL",
                "SUBGROUP",
                "GROUP",
                "DATE",
                "TIME",
                "CATEGORY",
                "NOTE",
                "AMOUNT",
                "INVOICED",
                "INVOICE_ID",
                "CATEGORY_NO_OF_UNITS",
                "CATEGORY_UNIT",
                "KIOSK",
                "KIOSK_QR_CODE",
                "TYPE",
                "BREAK",
                "NOTES",
                "BILLABLE_TOTAL",
                "RECEIPTS",
                "EXPENSE_TOTAL",
                "DATE_OF_CREATION",
                "DATE_OF_APPROVAL",
                "NAME",
                "ROLE",
                "PROJECTS",
                "STATUS",
                "WEEK_START",
                "WORKING_DAYS",
                "TEAM_MANAGERS",
                "TEAM_MEMBERS",
                "DAILY_WORK_CAPACITY",
                "VISIBILITY",
                "BILLABILITY",
                "TASKS",
                "TRACKED_H",
                "ESTIMATED_H",
                "REMAINING_H",
                "OVERAGE_H",
                "TRACKED_BUDGET",
                "ESTIMATED_BUDGET",
                "REMAINING_BUDGET",
                "OVERAGE_BUDGET",
                "PROGRESS",
                "RECURRING_ESTIMATE",
                "EXPENSES",
                "BILLABLE_EXPENSES",
                "NON_BILLABLE_EXPENSES",
                "ADDITIONAL_FIELDS",
                "PROJECT_MEMBERS",
                "PROJECT_MANAGER",
                "APPROVED_BY",
                "ISSUE_DATE",
                "DUE_ON",
                "BALANCE",
            ]
        ]
        | None
    ) = Field(default=None, alias="exportFields")
    file_id: str | None = Field(default=None, alias="fileId")
    file_name: str | None = Field(default=None, alias="fileName")
    id: str | None = None
    invoicing_info: invoicingInfo | None = Field(default=None, alias="invoicingInfo")
    locked: bool | None = None
    notes: str | None = None
    project_color: str | None = Field(default=None, alias="projectColor")
    project_id: str | None = Field(default=None, alias="projectId")
    project_name: str | None = Field(default=None, alias="projectName")
    quantity: float | None = None
    report_name: str | None = Field(default=None, alias="reportName")
    time: str | None = None
    user_email: str | None = Field(default=None, alias="userEmail")
    user_id: str | None = Field(default=None, alias="userId")
    user_name: str | None = Field(default=None, alias="userName")
    user_status: str | None = Field(default=None, alias="userStatus")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class ExpenseReportFilterV1(ClockifyRequestModel):
    approval_state: Literal["APPROVED", "UNAPPROVED", "ALL"] | None = Field(
        default=None, alias="approvalState"
    )
    billable: bool | None = None
    categories: ContainsArchivedFilterV1 | None = None
    clients: ContainsArchivedFilterV1 | None = None
    currency: ContainsArchivedFilterV1 | None = None
    date_range_end: str = Field(alias="dateRangeEnd")
    date_range_start: str = Field(alias="dateRangeStart")
    date_range_type: (
        Literal[
            "ABSOLUTE",
            "TODAY",
            "YESTERDAY",
            "THIS_WEEK",
            "LAST_WEEK",
            "PAST_TWO_WEEKS",
            "THIS_MONTH",
            "LAST_MONTH",
            "THIS_YEAR",
            "LAST_YEAR",
        ]
        | None
    ) = Field(default=None, alias="dateRangeType")
    export_type: Literal["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"] | None = Field(
        default=None, alias="exportType"
    )
    invoicing_state: Literal["INVOICED", "UNINVOICED", "ALL"] | None = Field(
        default=None, alias="invoicingState"
    )
    note: str | None = None
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    projects: ContainsArchivedFilterV1 | None = None
    sort_column: Literal["ID", "PROJECT", "USER", "CATEGORY", "DATE", "AMOUNT"] | None = Field(
        default=None, alias="sortColumn"
    )
    sort_order: Literal["ASCENDING", "DESCENDING"] | None = Field(default=None, alias="sortOrder")
    tasks: ContainsTaskFilterV1 | None = None
    time_zone: str | None = Field(default=None, alias="timeZone")
    user_groups: ContainsUsersFilterV1 | None = Field(default=None, alias="userGroups")
    user_locale: str | None = Field(default=None, alias="userLocale")
    users: ContainsUsersFilterV1 | None = None
    week_start: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="weekStart")
    without_note: bool | None = Field(default=None, alias="withoutNote")
    zoom_level: Literal["WEEK", "MONTH", "YEAR"] | None = Field(default=None, alias="zoomLevel")


class ExpenseTotalsDtoV1(ClockifyResponseModel):
    """Represents expense totals"""

    expenses_count: int | None = Field(default=None, alias="expensesCount")
    total_amount: float | None = Field(default=None, alias="totalAmount")
    total_amount_billable: float | None = Field(default=None, alias="totalAmountBillable")


class GroupOneDto(ClockifyResponseModel):
    amount: float | None = None
    children: list[GroupOneDto] | None = None
    client_name: str | None = Field(default=None, alias="clientName")
    days: list[DailyTotalDto] | None = None
    duration: float | None = None
    id: str | None = None
    name: str | None = None
    name_lower_case: str | None = Field(default=None, alias="nameLowerCase")


class ReportTagDto(ClockifyResponseModel):
    id: str | None = None
    name: str | None = None


class ReportTimeIntervalDto(ClockifyResponseModel):
    duration: int | None = None
    end: str | None = None
    start: str | None = None


class SummaryFilter(ClockifyRequestModel):
    """Summary report filter. Valid only on /reports/summary. At most three groups are allowed."""

    groups: list[SummaryGroup]
    sort_column: Literal["GROUP", "DURATION", "AMOUNT", "EARNED", "COST", "PROFIT"] | None = Field(
        default=None, alias="sortColumn"
    )
    summary_chart_type: Literal["BILLABILITY", "PROJECT"] | None = Field(
        default=None, alias="summaryChartType"
    )


# Allowed summary grouping key. Live reports also accept TAG grouping.
SummaryGroup = Literal[
    "CLIENT", "PROJECT", "USER", "WEEK", "DATE", "MONTH", "TIMEENTRY", "TASK", "TAG"
]


class SummaryReportRequest(ClockifyRequestModel):
    """Request payload for generating summary reports. Only summaryFilter is accepted as the report-specific filter."""

    amount_shown: Literal["EARNED", "COST", "PROFIT", "HIDE_AMOUNT", "EXPORT"] | None = Field(
        default=None, alias="amountShown"
    )
    amounts: list[AmountType] | None = None
    approval_state: Literal["APPROVED", "UNAPPROVED", "ALL"] | None = Field(
        default=None, alias="approvalState"
    )
    archived: bool | None = None
    billable: bool | None = None
    clients: ContainsArchivedFilter | None = None
    currency: ContainsArchivedFilter | None = None
    custom_fields: list[CustomFieldFilter] | None = Field(default=None, alias="customFields")
    date_format: str | None = Field(default=None, alias="dateFormat")
    date_range_end: str = Field(alias="dateRangeEnd")
    date_range_start: str = Field(alias="dateRangeStart")
    date_range_type: (
        Literal[
            "ABSOLUTE",
            "TODAY",
            "YESTERDAY",
            "THIS_WEEK",
            "LAST_WEEK",
            "PAST_TWO_WEEKS",
            "THIS_MONTH",
            "LAST_MONTH",
            "THIS_YEAR",
            "LAST_YEAR",
        ]
        | None
    ) = Field(default=None, alias="dateRangeType")
    description: str | None = None
    export_type: Literal["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"] | None = Field(
        default=None, alias="exportType"
    )
    invoicing_state: Literal["INVOICED", "UNINVOICED", "ALL"] | None = Field(
        default=None, alias="invoicingState"
    )
    projects: ContainsArchivedFilter | None = None
    rounding: bool | None = None
    sort_order: Literal["ASCENDING", "DESCENDING"] | None = Field(default=None, alias="sortOrder")
    summary_filter: SummaryFilter = Field(alias="summaryFilter")
    tags: ContainsTagFilter | None = None
    tasks: ContainsTaskFilter | None = None
    time_format: str | None = Field(default=None, alias="timeFormat")
    time_zone: str | None = Field(default=None, alias="timeZone")
    user_custom_fields: list[CustomFieldFilter] | None = Field(
        default=None, alias="userCustomFields"
    )
    user_groups: ContainsUsersFilter | None = Field(default=None, alias="userGroups")
    user_locale: str | None = Field(default=None, alias="userLocale")
    users: ContainsUsersFilter | None = None
    week_start: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="weekStart")
    without_description: bool | None = Field(default=None, alias="withoutDescription")
    zoom_level: Literal["WEEK", "MONTH", "YEAR"] | None = Field(default=None, alias="zoomLevel")


class SummaryReportResponseGroupTotals(ClockifyResponseModel):
    """Live summary report group total counters."""

    group_one_total_count: int | None = Field(default=None, alias="groupOneTotalCount")
    group_two_total_count: int | None = Field(default=None, alias="groupTwoTotalCount")


class SummaryReportResponse(ClockifyResponseModel):
    """Summary report response."""

    group_one: list[GroupOneDto] | None = Field(default=None, alias="groupOne")
    totals: list[TimeEntryReportTotals] | None = None
    donut_chart: list[dict[str, Any]] | None = Field(default=None, alias="donutChart")
    group_totals: SummaryReportResponseGroupTotals | None = Field(default=None, alias="groupTotals")


class TimeEntryDto(ClockifyResponseModel):
    approval_request_id: str | None = Field(default=None, alias="approvalRequestId")
    billable: bool | None = None
    client_id: str | None = Field(default=None, alias="clientId")
    client_name: str | None = Field(default=None, alias="clientName")
    description: str | None = None
    get_id: str | None = None
    id: str | None = None
    locked: bool | None = None
    project_color: str | None = Field(default=None, alias="projectColor")
    project_id: str | None = Field(default=None, alias="projectId")
    project_name: str | None = Field(default=None, alias="projectName")
    tags: list[ReportTagDto] | None = None
    task_id: str | None = Field(default=None, alias="taskId")
    task_name: str | None = Field(default=None, alias="taskName")
    time_interval: ReportTimeIntervalDto | None = Field(default=None, alias="timeInterval")
    user_email: str | None = Field(default=None, alias="userEmail")
    user_id: str | None = Field(default=None, alias="userId")
    user_name: str | None = Field(default=None, alias="userName")


class TimeEntryReportTotals(ClockifyResponseModel):
    amounts: list[AmountDto] | None = None
    entries_count: int | None = Field(default=None, alias="entriesCount")
    id: str | None = None
    total_billable_time: float | None = Field(default=None, alias="totalBillableTime")
    total_time: float | None = Field(default=None, alias="totalTime")


class UserDto(ClockifyResponseModel):
    date_format: str | None = Field(default=None, alias="dateFormat")
    email: str | None = None
    id: str | None = None
    name: str | None = None
    time_format: str | None = Field(default=None, alias="timeFormat")
    time_zone: str | None = Field(default=None, alias="timeZone")
    week_start: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="weekStart")


class WeeklyFilter(ClockifyRequestModel):
    """Weekly report filter. Valid only on /reports/weekly. The group is USER or PROJECT, and subgroup is always TIME."""

    group: Literal["USER", "PROJECT"]
    subgroup: Literal["TIME"]


class WeeklyReportRequest(ClockifyRequestModel):
    """Request payload for generating weekly reports. Only weeklyFilter is accepted as the report-specific filter."""

    amount_shown: Literal["EARNED", "COST", "PROFIT", "HIDE_AMOUNT", "EXPORT"] | None = Field(
        default=None, alias="amountShown"
    )
    amounts: list[AmountType] | None = None
    approval_state: Literal["APPROVED", "UNAPPROVED", "ALL"] | None = Field(
        default=None, alias="approvalState"
    )
    archived: bool | None = None
    billable: bool | None = None
    clients: ContainsArchivedFilter | None = None
    currency: ContainsArchivedFilter | None = None
    custom_fields: list[CustomFieldFilter] | None = Field(default=None, alias="customFields")
    date_format: str | None = Field(default=None, alias="dateFormat")
    date_range_end: str = Field(alias="dateRangeEnd")
    date_range_start: str = Field(alias="dateRangeStart")
    date_range_type: (
        Literal[
            "ABSOLUTE",
            "TODAY",
            "YESTERDAY",
            "THIS_WEEK",
            "LAST_WEEK",
            "PAST_TWO_WEEKS",
            "THIS_MONTH",
            "LAST_MONTH",
            "THIS_YEAR",
            "LAST_YEAR",
        ]
        | None
    ) = Field(default=None, alias="dateRangeType")
    description: str | None = None
    export_type: Literal["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"] | None = Field(
        default=None, alias="exportType"
    )
    invoicing_state: Literal["INVOICED", "UNINVOICED", "ALL"] | None = Field(
        default=None, alias="invoicingState"
    )
    projects: ContainsArchivedFilter | None = None
    rounding: bool | None = None
    sort_order: Literal["ASCENDING", "DESCENDING"] | None = Field(default=None, alias="sortOrder")
    tags: ContainsTagFilter | None = None
    tasks: ContainsTaskFilter | None = None
    time_format: str | None = Field(default=None, alias="timeFormat")
    time_zone: str | None = Field(default=None, alias="timeZone")
    user_custom_fields: list[CustomFieldFilter] | None = Field(
        default=None, alias="userCustomFields"
    )
    user_groups: ContainsUsersFilter | None = Field(default=None, alias="userGroups")
    user_locale: str | None = Field(default=None, alias="userLocale")
    users: ContainsUsersFilter | None = None
    week_start: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="weekStart")
    weekly_filter: WeeklyFilter = Field(alias="weeklyFilter")
    without_description: bool | None = Field(default=None, alias="withoutDescription")
    zoom_level: Literal["WEEK", "MONTH", "YEAR"] | None = Field(default=None, alias="zoomLevel")


class WeeklyReportResponse(ClockifyResponseModel):
    """Weekly report response."""

    decimal_format: bool | None = Field(default=None, alias="decimalFormat")
    group_one: list[GroupOneDto] | None = Field(default=None, alias="groupOne")
    include_users_without_time: bool | None = Field(default=None, alias="includeUsersWithoutTime")
    totals: list[TimeEntryReportTotals | None] | None = None
    totals_by_day: list[DailyTotalDto] | None = Field(default=None, alias="totalsByDay")
    track_time_down_to_seconds: bool | None = Field(default=None, alias="trackTimeDownToSeconds")
    users_without_time: list[UserDto] | None = Field(default=None, alias="usersWithoutTime")


class invoicingInfo(ClockifyResponseModel):
    """Expense's invoicing info."""

    invoice_id: str | None = Field(default=None, alias="invoiceId")
    manually_invoiced: bool | None = Field(default=None, alias="manuallyInvoiced")
