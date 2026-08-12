"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import (
    ContainsArchivedFilterRequest,
    ContainsOperator,
    InvoiceStatus,
    TaxType,
    VisibleZeroFieldsInvoice,
)


class BaseFilterRequest(ClockifyRequestModel):
    """Represents a base filter object."""

    contains: ContainsOperator | None = None
    ids: list[str] | None = None


class InvoiceCreateRequest(ClockifyRequestModel):
    client_id: str = Field(alias="clientId")
    currency: str
    due_date: str = Field(alias="dueDate")
    issued_date: str = Field(alias="issuedDate")
    number: str
    time_view_mode: TimeViewMode | None = Field(default=None, alias="timeViewMode")


class InvoiceCreateResponse(ClockifyResponseModel):
    bill_from: str | None = Field(default=None, alias="billFrom")
    client_id: str | None = Field(default=None, alias="clientId")
    currency: str | None = None
    due_date: str | None = Field(default=None, alias="dueDate")
    id: str | None = None
    issued_date: str | None = Field(default=None, alias="issuedDate")
    number: str | None = None


class InvoiceDtoV1(ClockifyResponseModel):
    """Represents an invoice summary."""

    amount: int | None = None
    balance: int | None = None
    client_id: str | None = Field(default=None, alias="clientId")
    client_name: str | None = Field(default=None, alias="clientName")
    currency: str | None = None
    due_date: str | None = Field(default=None, alias="dueDate")
    id: str | None = None
    issued_date: str | None = Field(default=None, alias="issuedDate")
    number: str | None = None
    paid: int | None = None
    status: InvoiceStatus | None = None


class InvoiceFilterRequest(ClockifyRequestModel):
    """Request body for filtering invoices."""

    clients: ContainsArchivedFilterRequest | None = None
    companies: BaseFilterRequest | None = None
    exact_amount: int | None = Field(default=None, alias="exactAmount")
    exact_balance: int | None = Field(default=None, alias="exactBalance")
    greater_than_amount: int | None = Field(default=None, alias="greaterThanAmount")
    greater_than_balance: int | None = Field(default=None, alias="greaterThanBalance")
    invoice_number: str | None = Field(default=None, alias="invoiceNumber")
    issue_date: TimeRangeRequestDtoV1 | None = Field(default=None, alias="issueDate")
    less_than_amount: int | None = Field(default=None, alias="lessThanAmount")
    less_than_balance: int | None = Field(default=None, alias="lessThanBalance")
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    sort_column: InvoiceSortColumn | None = Field(default=None, alias="sortColumn")
    sort_order: InvoicesSortOrder | None = Field(default=None, alias="sortOrder")
    statuses: list[InvoiceStatus] | None = None
    strict_search: bool | None = Field(default=None, alias="strictSearch")


class InvoiceInfoListResponse(ClockifyResponseModel):
    invoices: list[InvoiceInfoV1] | None = None
    total: int | None = None


class InvoiceInfoV1(ClockifyResponseModel):
    """Represents invoice info returned by filtered invoice search."""

    amount: int | None = None
    balance: int | None = None
    bill_from: str | None = Field(default=None, alias="billFrom")
    client_id: str | None = Field(default=None, alias="clientId")
    client_name: str | None = Field(default=None, alias="clientName")
    currency: str | None = None
    days_overdue: int | None = Field(default=None, alias="daysOverdue")
    due_date: str | None = Field(default=None, alias="dueDate")
    id: str | None = None
    issued_date: str | None = Field(default=None, alias="issuedDate")
    number: str | None = None
    paid: int | None = None
    status: InvoiceStatus | None = None
    visible_zero_fields: list[VisibleZeroFieldsInvoice] | None = Field(
        default=None, alias="visibleZeroFields"
    )


class InvoiceListResponse(ClockifyResponseModel):
    invoices: list[InvoiceDtoV1] | None = None
    total: int | None = None


# Invoice sorting column.
InvoiceSortColumn = Literal["ID", "CLIENT", "DUE_ON", "ISSUE_DATE", "AMOUNT", "BALANCE"]


class InvoiceStatusRequest(ClockifyRequestModel):
    invoice_status: InvoiceStatus = Field(alias="invoiceStatus")


# Sorting order.
InvoicesSortOrder = Literal["ASCENDING", "DESCENDING"]


class TimeRangeRequestDtoV1(ClockifyRequestModel):
    """Represents a time range object for invoice issue dates."""

    issue_date_end: str | None = Field(default=None, alias="issue-date-end")
    issue_date_start: str | None = Field(default=None, alias="issue-date-start")


TimeViewMode = Literal["TIME_SENSITIVE_VIEW", "AGGREGATED_TIME_VIEW"]


class UpdateInvoiceRequest(ClockifyRequestModel):
    bill_from: str | None = Field(default=None, alias="billFrom")
    client_address: str | None = Field(default=None, alias="clientAddress")
    client_id: str | None = Field(default=None, alias="clientId")
    company_id: str | None = Field(default=None, alias="companyId")
    currency: str
    discount_percent: float = Field(alias="discountPercent")
    due_date: str = Field(alias="dueDate")
    issued_date: str = Field(alias="issuedDate")
    note: str | None = None
    number: str
    subject: str | None = None
    tax2_percent: float = Field(alias="tax2Percent")
    tax_percent: float = Field(alias="taxPercent")
    tax_type: TaxType | None = Field(default=None, alias="taxType")
    visible_zero_fields: VisibleZeroFieldsInvoice | list[VisibleZeroFieldsInvoice] | None = Field(
        default=None, alias="visibleZeroFields"
    )
