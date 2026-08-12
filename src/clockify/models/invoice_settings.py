"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel
from clockify.models.common import TaxType


class InvoiceDefaultSettingsRequestV1(ClockifyRequestModel):
    """Represents an invoice default settings request object."""

    company_id: str | None = Field(default=None, alias="companyId")
    due_days: int | None = Field(default=None, alias="dueDays")
    item_type_id: str | None = Field(default=None, alias="itemTypeId")
    notes: str
    subject: str
    tax2_percent: float | None = Field(default=None, alias="tax2Percent")
    tax_percent: float | None = Field(default=None, alias="taxPercent")
    tax_type: TaxType | None = Field(default=None, alias="taxType")


class InvoiceExportFieldsRequest(ClockifyRequestModel):
    """Represents an invoice export fields request object."""

    item_type: bool | None = Field(default=None, alias="itemType")
    quantity: bool | None = None
    rtl: bool | None = None
    tax: bool | None = None
    tax2: bool | None = None
    unit_price: bool | None = Field(default=None, alias="unitPrice")


class InvoiceSettingsRequest(ClockifyRequestModel):
    """Request body for updating invoice settings/language labels."""

    defaults: InvoiceDefaultSettingsRequestV1 | None = None
    export_fields: InvoiceExportFieldsRequest | None = Field(default=None, alias="exportFields")
    labels: LabelsCustomizationRequest


class InvoiceSettingsResponse(ClockifyResponseModel):
    defaults: OpenapiInvoiceDefaultSettingsDto | None = None
    export_fields: OpenapiInvoiceExportFields | None = Field(default=None, alias="exportFields")
    labels: OpenapiLabelsCustomization | None = None


class LabelsCustomizationRequest(ClockifyRequestModel):
    """Represents a label customization request object."""

    amount: str
    bill_from: str = Field(alias="billFrom")
    bill_to: str = Field(alias="billTo")
    description: str
    discount: str
    due_date: str = Field(alias="dueDate")
    issue_date: str = Field(alias="issueDate")
    item_type: str = Field(alias="itemType")
    notes: str
    paid: str
    quantity: str
    subtotal: str
    tax: str
    tax2: str
    total: str
    total_amount_due: str = Field(alias="totalAmountDue")
    unit_price: str = Field(alias="unitPrice")


class OpenapiInvoiceDefaultSettingsDto(ClockifyResponseModel):
    """Represents an invoice default settings object."""

    company_id: str | None = Field(default=None, alias="companyId")
    default_import_expense_item_type_id: str | None = Field(
        default=None, alias="defaultImportExpenseItemTypeId"
    )
    default_import_time_item_type_id: str | None = Field(
        default=None, alias="defaultImportTimeItemTypeId"
    )
    due_days: int | None = Field(default=None, alias="dueDays")
    item_type: str | None = Field(default=None, alias="itemType")
    item_type_id: str | None = Field(default=None, alias="itemTypeId")
    notes: str | None = None
    subject: str | None = None
    tax: int | None = None
    tax2: int | None = None
    tax2_percent: float | None = Field(default=None, alias="tax2Percent")
    tax_percent: float | None = Field(default=None, alias="taxPercent")
    tax_type: Literal["COMPOUND", "SIMPLE", "NONE"] | None = Field(default=None, alias="taxType")


class OpenapiInvoiceExportFields(ClockifyResponseModel):
    """Represents an invoice export fields object."""

    rtl_upper: bool | None = Field(default=None, alias="RTL")
    item_type: bool | None = Field(default=None, alias="itemType")
    quantity: bool | None = None
    rtl: bool | None = None
    tax: bool | None = None
    tax2: bool | None = None
    unit_price: bool | None = Field(default=None, alias="unitPrice")


class OpenapiLabelsCustomization(ClockifyResponseModel):
    """Represents a label customization object."""

    amount: str | None = None
    bill_from: str | None = Field(default=None, alias="billFrom")
    bill_to: str | None = Field(default=None, alias="billTo")
    description: str | None = None
    discount: str | None = None
    due_date: str | None = Field(default=None, alias="dueDate")
    issue_date: str | None = Field(default=None, alias="issueDate")
    item_type: str | None = Field(default=None, alias="itemType")
    notes: str | None = None
    paid: str | None = None
    quantity: str | None = None
    subtotal: str | None = None
    tax: str | None = None
    tax2: str | None = None
    total: str | None = None
    total_amount: str | None = Field(default=None, alias="totalAmount")
    unit_price: str | None = Field(default=None, alias="unitPrice")
