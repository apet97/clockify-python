"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel

# Represents item applyTaxes type.
ApplyTaxes = Literal["TAX1", "TAX2", "TAX1TAX2", "NONE"]


class AutomaticLockDtoV1(ClockifyResponseModel):
    """Represents an automatic lock object."""

    change_day: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="changeDay")
    day_of_month: int | None = Field(default=None, alias="dayOfMonth")
    first_day: (
        Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"] | None
    ) = Field(default=None, alias="firstDay")
    older_than_period: Literal["DAYS", "WEEKS", "MONTHS"] | None = Field(
        default=None, alias="olderThanPeriod"
    )
    older_than_value: int | None = Field(default=None, alias="olderThanValue")
    type: Literal["WEEKLY", "MONTHLY", "OLDER_THAN"] | None = None


class AutomaticTimeEntryCreationRequest(ClockifyRequestModel):
    """Provides automatic time entry creation settings."""

    default_entities: PoliciesDefaultEntitiesRequest = Field(alias="defaultEntities")
    enabled: bool | None = None


# Represents whether tax is calculated as item based or invoice based.
CalculationType = Literal["INVOICE_BASED", "ITEM_BASED"]


class ContainsArchivedFilterRequest(ClockifyRequestModel):
    """Represents a filter for imported items that can include archived entities."""

    contains: ContainsOperator | None = None
    ids: list[str] | None = None
    status: EntityStatus | None = None


# Filter type.
ContainsOperator = Literal["CONTAINS", "DOES_NOT_CONTAIN", "CONTAINS_ONLY"]

Currency = str


class CurrencyWithDefaultInfoDtoV1(ClockifyResponseModel):
    """Represents currency with default info object."""

    code: str | None = None
    id: str | None = None
    is_default: bool | None = Field(default=None, alias="isDefault")


DayOfWeek = Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


class EntityCreationPermission(ClockifyResponseModel):
    """Represents an entity creation permission enum with optional creators."""

    creators: list[str] | None = None
    value: Literal["ADMINS", "ADMINS_AND_PROJECT_MANAGERS", "EVERYONE"] | None = None


class EntityCreationPermissionsDtoV1(ClockifyResponseModel):
    """Represents an entity creation permission object."""

    who_can_create_projects_and_clients: EntityCreationPermission | None = Field(
        default=None, alias="whoCanCreateProjectsAndClients"
    )
    who_can_create_tags: EntityCreationPermission | None = Field(
        default=None, alias="whoCanCreateTags"
    )
    who_can_create_tasks: EntityCreationPermission | None = Field(
        default=None, alias="whoCanCreateTasks"
    )


# Filters entities by status.
EntityStatus = Literal["ACTIVE", "ARCHIVED", "ALL"]


class ExpenseCategoryDto(ClockifyResponseModel):
    archived: bool | None = None
    has_unit_price: bool | None = Field(default=None, alias="hasUnitPrice")
    id: str | None = None
    name: str | None = None
    price_in_cents: int | None = Field(default=None, alias="priceInCents")
    unit: str | None = None
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class InvoiceDtoFull(ClockifyResponseModel):
    """Represents a complete invoice object."""

    amount: int | None = None
    balance: int | None = None
    bill_from: str | None = Field(default=None, alias="billFrom")
    calculation_type: CalculationType | None = Field(default=None, alias="calculationType")
    client_address: str | None = Field(default=None, alias="clientAddress")
    client_id: str | None = Field(default=None, alias="clientId")
    client_name: str | None = Field(default=None, alias="clientName")
    company_id: str | None = Field(default=None, alias="companyId")
    contains_imported_expenses: bool | None = Field(default=None, alias="containsImportedExpenses")
    contains_imported_times: bool | None = Field(default=None, alias="containsImportedTimes")
    currency: str | None = None
    discount: float | None = None
    discount_amount: int | None = Field(default=None, alias="discountAmount")
    due_date: str | None = Field(default=None, alias="dueDate")
    id: str | None = None
    issued_date: str | None = Field(default=None, alias="issuedDate")
    items: list[InvoiceItemDto] | None = None
    note: str | None = None
    number: str | None = None
    paid: int | None = None
    status: InvoiceStatus | None = None
    subject: str | None = None
    subtotal: int | None = None
    tax: float | None = None
    tax2: float | None = None
    tax2_amount: int | None = Field(default=None, alias="tax2Amount")
    tax_amount: int | None = Field(default=None, alias="taxAmount")
    tax_type: TaxType | None = Field(default=None, alias="taxType")
    user_id: str | None = Field(default=None, alias="userId")
    visible_zero_fields: list[VisibleZeroFieldsInvoice] | None = Field(
        default=None, alias="visibleZeroFields"
    )


# Represents the invoice item import type.
InvoiceImportType = Literal["NOT_IMPORTED", "TIME_ENTRY_IMPORT", "EXPENSE_IMPORT"]


class InvoiceItemDto(ClockifyResponseModel):
    """Represents an invoice item data transfer object."""

    amount: int | None = None
    apply_taxes: ApplyTaxes | None = Field(default=None, alias="applyTaxes")
    description: str | None = None
    expense_ids: list[str] | None = Field(default=None, alias="expenseIds")
    import_type: InvoiceImportType | None = Field(default=None, alias="importType")
    item_type: str | None = Field(default=None, alias="itemType")
    order: int | None = None
    quantity: int | None = None
    time_entry_ids: list[str] | None = Field(default=None, alias="timeEntryIds")
    unit_price: int | None = Field(default=None, alias="unitPrice")


# Represents the live status of an invoice. DRAFT is rejected by Clockify; use UNSENT for draft-like invoices.
InvoiceStatus = Literal["UNSENT", "SENT", "PAID", "PARTIALLY_PAID", "VOID", "OVERDUE"]


class PoliciesDefaultEntitiesRequest(ClockifyRequestModel):
    """Default project and task for automatically created time entries."""

    project_id: str | None = Field(default=None, alias="projectId")
    task_id: str | None = Field(default=None, alias="taskId")


class ProjectInfoDto(ClockifyResponseModel):
    """Represents a project info object."""

    client_id: str | None = Field(default=None, alias="clientId")
    client_name: str | None = Field(default=None, alias="clientName")
    color: str | None = None
    id: str | None = None
    name: str | None = None


class RateDto(ClockifyResponseModel):
    """Represents hourly rate object."""

    amount: int | None = None
    currency: str | None = None


class RoundDto(ClockifyResponseModel):
    """Represents a time rounding object."""

    minutes: str | None = None
    round: str | None = None


SortOrder = Literal["ASCENDING", "DESCENDING"]


class TaskInfoDto(ClockifyResponseModel):
    """Represents a task info object."""

    id: str | None = None
    name: str | None = None


# Represents an invoice taxation type.
TaxType = Literal["COMPOUND", "SIMPLE", "NONE"]


class UpdateCostRateRequest(ClockifyRequestModel):
    amount: int
    since: str | None = None


class UpsertUserCustomFieldRequest(ClockifyRequestModel):
    custom_field_id: str = Field(alias="customFieldId")
    value: Any | None = None


# Represents custom field type.
UsersCustomFieldType = Literal[
    "TXT", "NUMBER", "DROPDOWN_SINGLE", "DROPDOWN_MULTIPLE", "CHECKBOX", "LINK"
]

# Represents a day of the week.
UsersDayOfWeek = Literal[
    "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"
]

# Represents a zero-value invoice field that will be visible.
VisibleZeroFieldsInvoice = Literal["TAX", "TAX_2", "DISCOUNT"]


class Workspace(ClockifyResponseModel):
    """Workspace object."""

    cake_organization_id: str | None = Field(default=None, alias="cakeOrganizationId")
    cost_rate: WorkspacesRateDtoV1 | None = Field(default=None, alias="costRate")
    currencies: list[CurrencyWithDefaultInfoDtoV1] | None = None
    feature_subscription_type: str | None = Field(default=None, alias="featureSubscriptionType")
    features: list[WorkspacesFeature] | None = None
    hourly_rate: WorkspacesRateDtoV1 | None = Field(default=None, alias="hourlyRate")
    id: str | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    memberships: list[WorkspacesMembershipDtoV1] | None = None
    name: str | None = None
    subdomain: WorkspaceSubdomainDtoV1 | None = None
    workspace_settings: WorkspaceSettingsDtoV1 | None = Field(
        default=None, alias="workspaceSettings"
    )


class WorkspaceSettingsDtoV1(ClockifyResponseModel):
    """Workspace settings. Time Duration Format can be set by durationFormat; the decimalFormat and trackTimeDownToSecond booleans are deprecated in the source documentation."""

    active_billable_hours: bool | None = Field(default=None, alias="activeBillableHours")
    admin_only_pages: list[Literal["PROJECT", "TEAM", "REPORTS"]] | None = Field(
        default=None, alias="adminOnlyPages"
    )
    automatic_lock: AutomaticLockDtoV1 | None = Field(default=None, alias="automaticLock")
    can_see_time_sheet: bool | None = Field(default=None, alias="canSeeTimeSheet")
    can_see_tracker: bool | None = Field(default=None, alias="canSeeTracker")
    currency_format: (
        Literal["CURRENCY_SPACE_VALUE", "VALUE_SPACE_CURRENCY", "CURRENCY_VALUE", "VALUE_CURRENCY"]
        | None
    ) = Field(default=None, alias="currencyFormat")
    default_billable_projects: bool | None = Field(default=None, alias="defaultBillableProjects")
    duration_format: Literal["FULL", "COMPACT", "DECIMAL"] | None = Field(
        default=None, alias="durationFormat"
    )
    entity_creation_permissions: EntityCreationPermissionsDtoV1 | None = Field(
        default=None, alias="entityCreationPermissions"
    )
    force_description: bool | None = Field(default=None, alias="forceDescription")
    force_projects: bool | None = Field(default=None, alias="forceProjects")
    force_tags: bool | None = Field(default=None, alias="forceTags")
    force_tasks: bool | None = Field(default=None, alias="forceTasks")
    is_project_public_by_default: bool | None = Field(
        default=None, alias="isProjectPublicByDefault"
    )
    lock_time_entries: str | None = Field(default=None, alias="lockTimeEntries")
    lock_time_zone: str | None = Field(default=None, alias="lockTimeZone")
    multi_factor_enabled: bool | None = Field(default=None, alias="multiFactorEnabled")
    number_format: (
        Literal["COMMA_PERIOD", "PERIOD_COMMA", "QUOTATION_MARK_PERIOD", "SPACE_COMMA"] | None
    ) = Field(default=None, alias="numberFormat")
    only_admins_can_change_billable_status: bool | None = Field(
        default=None, alias="onlyAdminsCanChangeBillableStatus"
    )
    only_admins_create_project: bool | None = Field(default=None, alias="onlyAdminsCreateProject")
    only_admins_create_tag: bool | None = Field(default=None, alias="onlyAdminsCreateTag")
    only_admins_create_task: bool | None = Field(default=None, alias="onlyAdminsCreateTask")
    only_admins_see_all_time_entries: bool | None = Field(
        default=None, alias="onlyAdminsSeeAllTimeEntries"
    )
    only_admins_see_billable_rates: bool | None = Field(
        default=None, alias="onlyAdminsSeeBillableRates"
    )
    only_admins_see_dashboard: bool | None = Field(default=None, alias="onlyAdminsSeeDashboard")
    only_admins_see_public_projects_entries: bool | None = Field(
        default=None, alias="onlyAdminsSeePublicProjectsEntries"
    )
    project_favorites: bool | None = Field(default=None, alias="projectFavorites")
    project_grouping_label: str | None = Field(default=None, alias="projectGroupingLabel")
    project_label: str | None = Field(default=None, alias="projectLabel")
    project_picker_special_filter: bool | None = Field(
        default=None, alias="projectPickerSpecialFilter"
    )
    round: RoundDto | None = None
    task_label: str | None = Field(default=None, alias="taskLabel")
    time_rounding_in_reports: bool | None = Field(default=None, alias="timeRoundingInReports")
    time_tracking_mode: Literal["DEFAULT", "STOPWATCH_ONLY"] | None = Field(
        default=None, alias="timeTrackingMode"
    )
    track_time_down_to_second: bool | None = Field(default=None, alias="trackTimeDownToSecond")
    working_days: (
        list[Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]]
        | None
    ) = Field(default=None, alias="workingDays")


class WorkspaceSubdomainDtoV1(ClockifyResponseModel):
    """Represents the workspace subdomain."""

    enabled: bool | None = None
    name: str | None = None


# Workspace feature identifier.
WorkspacesFeature = Literal[
    "ADD_TIME_FOR_OTHERS",
    "ADMIN_PANEL",
    "ALERTS",
    "APPROVAL",
    "AUDIT_LOG",
    "AUTOMATIC_LOCK",
    "BRANDED_REPORTS",
    "BULK_EDIT",
    "CUSTOM_FIELDS",
    "CUSTOM_REPORTING",
    "CUSTOM_SUBDOMAIN",
    "CREATION_PERMISSIONS",
    "DECIMAL_FORMAT",
    "DISABLE_MANUAL_MODE",
    "EDIT_MEMBER_PROFILE",
    "EXCLUDE_NON_BILLABLE_FROM_ESTIMATE",
    "EXPENSES",
    "FILE_IMPORT",
    "TIMESHEET_IMPORT",
    "USER_IMPORT",
    "HIDE_PAGES",
    "HISTORIC_RATES",
    "INVOICING",
    "INVOICE_EMAILS",
    "INVOICE_REMINDERS",
    "LABOR_COST",
    "LOCATIONS",
    "MANAGER_ROLE",
    "MULTI_FACTOR_AUTHENTICATION",
    "PROJECT_BUDGET",
    "PROJECT_TEMPLATES",
    "GRANT_PROJECT_MANAGER_ROLE",
    "PRIVATE_PROJECT_ACCESS",
    "QUICKBOOKS_INTEGRATION",
    "RECURRING_ESTIMATES",
    "RECURRING_INVOICES",
    "REQUIRED_FIELDS",
    "SCHEDULED_REPORTS",
    "SCHEDULING",
    "SCREENSHOTS",
    "SSO",
    "SUMMARY_ESTIMATE",
    "TARGETS_AND_REMINDERS",
    "TASK_RATES",
    "TIME_OFF",
    "UNLIMITED_REPORTS",
    "USER_CUSTOM_FIELDS",
    "WHO_CAN_CHANGE_TIMEENTRY_BILLABILITY",
    "BREAKS",
    "KIOSK_SESSION_DURATION",
    "KIOSK_PIN_REQUIRED",
    "WHO_CAN_SEE_ALL_TIME_ENTRIES",
    "WHO_CAN_SEE_PROJECT_STATUS",
    "WHO_CAN_SEE_PUBLIC_PROJECTS_ENTRIES",
    "WHO_CAN_SEE_TEAMS_DASHBOARD",
    "WORKSPACE_LOCK_TIMEENTRIES",
    "WORKSPACE_TIME_AUDIT",
    "WORKSPACE_TIME_ROUNDING",
    "KIOSK",
    "KIOSK_SIX_DIGIT_PIN",
    "KIOSK_QR_CODE",
    "LIMITED_USERS",
    "FORECASTING",
    "TIME_TRACKING",
    "ATTENDANCE_REPORT",
    "WORKSPACE_TRANSFER",
    "FAVORITE_ENTRIES",
    "SPLIT_TIME_ENTRY",
    "CLIENT_CURRENCY",
    "SCHEDULING_FORECASTING",
    "SCIM",
    "UNLIMITED_USER_SEATS",
    "BILLABLE_HOURS",
    "PROJECT_ESTIMATE",
    "CSV_EXPORT",
    "XLSX_EXPORT",
    "ONE_MONTH_RANGE_REPORTS",
    "ONE_YEAR_RANGE_REPORTS",
    "SHARED_REPORTS",
]


class WorkspacesMembershipDtoV1(ClockifyResponseModel):
    """Represents a membership object."""

    cost_rate: WorkspacesRateDtoV1 | None = Field(default=None, alias="costRate")
    hourly_rate: WorkspacesRateDtoV1 | None = Field(default=None, alias="hourlyRate")
    membership_status: Literal["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"] | None = Field(
        default=None, alias="membershipStatus"
    )
    membership_type: Literal["WORKSPACE", "PROJECT", "USERGROUP"] | None = Field(
        default=None, alias="membershipType"
    )
    target_id: str | None = Field(default=None, alias="targetId")
    user_id: str | None = Field(default=None, alias="userId")


class WorkspacesRateDtoV1(ClockifyResponseModel):
    """Represents hourly rate object."""

    amount: int | None = None
    currency: str | None = None
