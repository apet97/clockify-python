"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class AddInvoicePaymentRequest(ClockifyRequestModel):
    amount: int
    note: str | None = None
    payment_date: str | None = Field(default=None, alias="paymentDate")


class InvoicePaymentDto(ClockifyResponseModel):
    """Represents an invoice payment."""

    amount: int | None = None
    author: str | None = None
    date: str | None = None
    id: str | None = None
    note: str | None = None
