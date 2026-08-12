"""Invoice items resource: explicit methods over the invoice-item operations."""

from collections.abc import Mapping
from typing import Any

from clockify.models import AddInvoiceItemRequest, ImportInvoiceItemsRequest, InvoiceDtoFull
from clockify.operations.invoice_items import (
    INVOICE_ITEMS_CREATE,
    INVOICE_ITEMS_DELETE,
    INVOICE_ITEMS_IMPORT_ITEMS,
)
from clockify.resources._base import ResourceBase


class InvoiceItemsResource(ResourceBase):
    async def create(
        self,
        invoice_id: str,
        body: "AddInvoiceItemRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> InvoiceDtoFull:
        """unitPrice is minor units x100; returns the full updated invoice, not the item."""
        validated = self._coerce(body, AddInvoiceItemRequest)
        response = await self._call(
            INVOICE_ITEMS_CREATE,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
            body=validated,
        )
        return self._adapt(INVOICE_ITEMS_CREATE, response, InvoiceDtoFull)

    async def delete(
        self, invoice_id: str, order: "int | str", *, workspace_id: str | None = None
    ) -> InvoiceDtoFull:
        """`order` is the 1-based item order (not an id); returns the full updated invoice."""
        response = await self._call(
            INVOICE_ITEMS_DELETE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "invoiceId": invoice_id,
                "order": str(order),
            },
        )
        return self._adapt(INVOICE_ITEMS_DELETE, response, InvoiceDtoFull)

    async def import_items(
        self,
        invoice_id: str,
        body: "ImportInvoiceItemsRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> InvoiceDtoFull:
        """unitPrice on imported items is minor units x100 (amount = unitPrice*quantity/100)."""
        validated = self._coerce(body, ImportInvoiceItemsRequest)
        response = await self._call(
            INVOICE_ITEMS_IMPORT_ITEMS,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
            body=validated,
        )
        return self._adapt(INVOICE_ITEMS_IMPORT_ITEMS, response, InvoiceDtoFull)
