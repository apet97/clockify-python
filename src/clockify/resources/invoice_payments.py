"""Invoice payments resource: explicit methods over the invoice-payment operations."""

import builtins
from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import AddInvoicePaymentRequest, InvoiceDtoFull, InvoicePaymentDto
from clockify.operations.invoice_payments import (
    INVOICE_PAYMENTS_CREATE,
    INVOICE_PAYMENTS_DELETE,
    INVOICE_PAYMENTS_LIST,
)
from clockify.resources._base import ResourceBase

_PAYMENT_LIST = TypeAdapter(list[InvoicePaymentDto])


class InvoicePaymentsResource(ResourceBase):
    async def create(
        self,
        invoice_id: str,
        body: "AddInvoicePaymentRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> InvoiceDtoFull:
        """Returns the updated INVOICE, not the payment — recover the payment id by
        diffing `list()` before/after. `amount` is MINOR units (cents), minimum 1."""
        validated = self._coerce(body, AddInvoicePaymentRequest)
        response = await self._call(
            INVOICE_PAYMENTS_CREATE,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
            body=validated,
        )
        return self._adapt(INVOICE_PAYMENTS_CREATE, response, InvoiceDtoFull)

    async def delete(
        self, invoice_id: str, payment_id: str, *, workspace_id: str | None = None
    ) -> InvoiceDtoFull:
        response = await self._call(
            INVOICE_PAYMENTS_DELETE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "invoiceId": invoice_id,
                "paymentId": payment_id,
            },
        )
        return self._adapt(INVOICE_PAYMENTS_DELETE, response, InvoiceDtoFull)

    async def list(
        self,
        invoice_id: str,
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> builtins.list[InvoicePaymentDto]:
        response = await self._call(
            INVOICE_PAYMENTS_LIST,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
            query={"page": page, "page_size": page_size},
        )
        return self._adapt(INVOICE_PAYMENTS_LIST, response, _PAYMENT_LIST)
