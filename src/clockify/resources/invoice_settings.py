"""Invoice settings resource: explicit methods over the invoice-settings operations."""

from collections.abc import Mapping
from typing import Any

from clockify.models import InvoiceSettingsRequest, InvoiceSettingsResponse
from clockify.operations.invoice_settings import (
    INVOICE_SETTINGS_GET,
    INVOICE_SETTINGS_UPDATE,
)
from clockify.resources._base import ResourceBase


class InvoiceSettingsResource(ResourceBase):
    async def get(self, *, workspace_id: str | None = None) -> InvoiceSettingsResponse:
        response = await self._call(
            INVOICE_SETTINGS_GET, path={"workspaceId": self._workspace(workspace_id)}
        )
        return self._adapt(INVOICE_SETTINGS_GET, response, InvoiceSettingsResponse)

    async def update(
        self,
        body: "InvoiceSettingsRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> None:
        """Workspace-wide full replacement; success is 200 with an empty body."""
        validated = self._coerce(body, InvoiceSettingsRequest)
        await self._call(
            INVOICE_SETTINGS_UPDATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return None
