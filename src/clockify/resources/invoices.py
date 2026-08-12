"""Invoices resource: explicit methods over the invoice operations."""

from collections.abc import Mapping
from typing import Any

from clockify.models import (
    InvoiceCreateRequest,
    InvoiceCreateResponse,
    InvoiceDtoFull,
    InvoiceFilterRequest,
    InvoiceInfoListResponse,
    InvoiceListResponse,
    InvoiceStatusRequest,
    UpdateInvoiceRequest,
)
from clockify.operations.invoices import (
    INVOICES_CREATE,
    INVOICES_DELETE,
    INVOICES_DUPLICATE,
    INVOICES_EXPORT,
    INVOICES_FILTER,
    INVOICES_GET,
    INVOICES_LIST,
    INVOICES_UPDATE,
    INVOICES_UPDATE_STATUS,
)
from clockify.resources._base import ResourceBase
from clockify.response import BinaryResponse


class InvoicesResource(ResourceBase):
    async def create(
        self,
        body: "InvoiceCreateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> InvoiceCreateResponse:
        """POST silently drops note/subject — create the draft, then set them via update. Money fields are minor units (cents)."""
        validated = self._coerce(body, InvoiceCreateRequest)
        response = await self._call(
            INVOICES_CREATE, path={"workspaceId": self._workspace(workspace_id)}, body=validated
        )
        return self._adapt(INVOICES_CREATE, response, InvoiceCreateResponse)

    async def delete(self, invoice_id: str, *, workspace_id: str | None = None) -> None:
        await self._call(
            INVOICES_DELETE,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
        )
        return None

    async def duplicate(
        self, invoice_id: str, *, workspace_id: str | None = None
    ) -> InvoiceDtoFull:
        """Item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100."""
        response = await self._call(
            INVOICES_DUPLICATE,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
        )
        return self._adapt(INVOICES_DUPLICATE, response, InvoiceDtoFull)

    async def export(
        self,
        invoice_id: str,
        *,
        workspace_id: str | None = None,
        user_locale: str | None = None,
    ) -> BinaryResponse:
        """Binary invoice export; live Clockify requires userLocale (default en-US)."""
        response = await self._call(
            INVOICES_EXPORT,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
            query={"user_locale": user_locale},
        )
        return response.data

    async def filter(
        self,
        body: "InvoiceFilterRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> InvoiceInfoListResponse:
        """Non-mutating POST — a read that carries its filter in a JSON body."""
        validated = self._coerce(body, InvoiceFilterRequest)
        response = await self._call(
            INVOICES_FILTER, path={"workspaceId": self._workspace(workspace_id)}, body=validated
        )
        return self._adapt(INVOICES_FILTER, response, InvoiceInfoListResponse)

    async def get(self, invoice_id: str, *, workspace_id: str | None = None) -> InvoiceDtoFull:
        """A deleted or never-existing id returns 400 code 501, never 404."""
        response = await self._call(
            INVOICES_GET,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
        )
        return self._adapt(INVOICES_GET, response, InvoiceDtoFull)

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        statuses: list[str] | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
    ) -> InvoiceListResponse:
        response = await self._call(
            INVOICES_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "page": page,
                "page_size": page_size,
                "statuses": statuses,
                "sort_column": sort_column,
                "sort_order": sort_order,
            },
        )
        return self._adapt(INVOICES_LIST, response, InvoiceListResponse)

    async def update(
        self,
        invoice_id: str,
        body: "UpdateInvoiceRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> InvoiceDtoFull:
        """Full replacement — omitted fields are dropped; GET returns tax/tax2/discount x100-scaled, but this PUT wants plain percents in taxPercent/tax2Percent/discountPercent."""
        validated = self._coerce(body, UpdateInvoiceRequest)
        response = await self._call(
            INVOICES_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
            body=validated,
        )
        return self._adapt(INVOICES_UPDATE, response, InvoiceDtoFull)

    async def update_status(
        self,
        invoice_id: str,
        body: "InvoiceStatusRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> None:
        validated = self._coerce(body, InvoiceStatusRequest)
        await self._call(
            INVOICES_UPDATE_STATUS,
            path={"workspaceId": self._workspace(workspace_id), "invoiceId": invoice_id},
            body=validated,
        )
        return None
