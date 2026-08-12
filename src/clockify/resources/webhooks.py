"""Webhooks resource: explicit methods over the webhook operations."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    WebhookCollectionDtoV1,
    WebhookDtoV1,
    WebhookEventStatusWithLatestLogDtoV1,
    WebhookLogDtoV1,
    WebhookLogsRequest,
    WebhookRequest,
    WebhooksWebhook2,
)
from clockify.operations.webhooks import (
    WEBHOOKS_CREATE,
    WEBHOOKS_DELETE,
    WEBHOOKS_GET,
    WEBHOOKS_LIST,
    WEBHOOKS_LIST_EVENT_STATUSES,
    WEBHOOKS_LIST_FOR_ADDON,
    WEBHOOKS_ROTATE_TOKEN,
    WEBHOOKS_SEARCH_LOGS,
    WEBHOOKS_UPDATE,
)
from clockify.resources._base import ResourceBase

_EVENT_STATUS_LIST = TypeAdapter(list[WebhookEventStatusWithLatestLogDtoV1])
_LOG_LIST = TypeAdapter(list[WebhookLogDtoV1])


ListOfStr = list[str]
ListOfWebhookEventStatusWithLatestLogDtoV1 = list[WebhookEventStatusWithLatestLogDtoV1]
ListOfWebhookLogDtoV1 = list[WebhookLogDtoV1]


class WebhooksResource(ResourceBase):
    async def create(
        self,
        body: "WebhookRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> WebhookDtoV1:
        """`name` is required under X-Api-Key auth but not under X-Addon-Token."""
        validated = self._coerce(body, WebhookRequest)
        response = await self._call(
            WEBHOOKS_CREATE, path={"workspaceId": self._workspace(workspace_id)}, body=validated
        )
        return self._adapt(WEBHOOKS_CREATE, response, WebhookDtoV1)

    async def delete(self, webhook_id: str, *, workspace_id: str | None = None) -> None:
        await self._call(
            WEBHOOKS_DELETE,
            path={"workspaceId": self._workspace(workspace_id), "webhookId": webhook_id},
        )
        return None

    async def get(self, webhook_id: str, *, workspace_id: str | None = None) -> WebhookDtoV1:
        response = await self._call(
            WEBHOOKS_GET,
            path={"workspaceId": self._workspace(workspace_id), "webhookId": webhook_id},
        )
        return self._adapt(WEBHOOKS_GET, response, WebhookDtoV1)

    async def list(
        self, *, workspace_id: str | None = None, type: str | None = None
    ) -> WebhookCollectionDtoV1:
        """Items live under the `webhooks` envelope key."""
        response = await self._call(
            WEBHOOKS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={"type": type},
        )
        return self._adapt(WEBHOOKS_LIST, response, WebhookCollectionDtoV1)

    async def list_event_statuses(
        self,
        webhook_id: str,
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        size: int | None = None,
        statuses: "ListOfStr | None" = None,
    ) -> "ListOfWebhookEventStatusWithLatestLogDtoV1":
        response = await self._call(
            WEBHOOKS_LIST_EVENT_STATUSES,
            path={"workspaceId": self._workspace(workspace_id), "webhookId": webhook_id},
            query={"page": page, "size": size, "statuses": statuses},
        )
        return self._adapt(WEBHOOKS_LIST_EVENT_STATUSES, response, _EVENT_STATUS_LIST)

    async def list_for_addon(
        self, addon_id: str, *, workspace_id: str | None = None
    ) -> WebhookCollectionDtoV1:
        """Items live under the `webhooks` envelope key."""
        response = await self._call(
            WEBHOOKS_LIST_FOR_ADDON,
            path={"workspaceId": self._workspace(workspace_id), "addonId": addon_id},
        )
        return self._adapt(WEBHOOKS_LIST_FOR_ADDON, response, WebhookCollectionDtoV1)

    async def rotate_token(
        self, webhook_id: str, *, workspace_id: str | None = None
    ) -> WebhooksWebhook2:
        """Body-less PATCH that regenerates the webhook token; old token stops working."""
        response = await self._call(
            WEBHOOKS_ROTATE_TOKEN,
            path={"workspaceId": self._workspace(workspace_id), "webhookId": webhook_id},
        )
        return self._adapt(WEBHOOKS_ROTATE_TOKEN, response, WebhooksWebhook2)

    async def search_logs(
        self,
        webhook_id: str,
        body: "WebhookLogsRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> "ListOfWebhookLogDtoV1":
        """Non-mutating log-search POST; pagination via page/size query parameters."""
        validated = self._coerce(body, WebhookLogsRequest)
        response = await self._call(
            WEBHOOKS_SEARCH_LOGS,
            path={"workspaceId": self._workspace(workspace_id), "webhookId": webhook_id},
            query={"page": page, "size": size},
            body=validated,
        )
        return self._adapt(WEBHOOKS_SEARCH_LOGS, response, _LOG_LIST)

    async def update(
        self,
        webhook_id: str,
        body: "WebhookRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> WebhookDtoV1:
        """PUT omission behavior is unproven; treat as a potential full replacement."""
        validated = self._coerce(body, WebhookRequest)
        response = await self._call(
            WEBHOOKS_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "webhookId": webhook_id},
            body=validated,
        )
        return self._adapt(WEBHOOKS_UPDATE, response, WebhookDtoV1)
