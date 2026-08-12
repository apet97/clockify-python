# pyright: reportUnusedFunction=false
"""Raw read tools: webhooks (5 reads)."""

from typing import Any

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_webhooks_get", annotations=READ_ANNOTATIONS)
    async def clockify_webhooks_get(webhook_id: str, workspace_id: str | None = None) -> ReadResult:
        """Get one webhook by ID."""
        return await raw_read(
            client,
            "getWebhookById",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "webhookId": webhook_id,
            },
        )

    @server.tool(name="clockify_webhooks_list", annotations=READ_ANNOTATIONS)
    async def clockify_webhooks_list(
        workspace_id: str | None = None,
        type: str | None = None,
    ) -> ReadResult:
        """List webhooks on the workspace, optionally filtered by `type`."""
        return await raw_read(
            client,
            "getWebhooksOnWorkspace",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={"type": type},
        )

    @server.tool(name="clockify_webhooks_list_event_statuses", annotations=READ_ANNOTATIONS)
    async def clockify_webhooks_list_event_statuses(
        webhook_id: str,
        workspace_id: str | None = None,
        page: int | None = None,
        size: int | None = None,
        statuses: str | None = None,
    ) -> ReadResult:
        """List a webhook's event statuses with the latest delivery log per event."""
        return await raw_read(
            client,
            "getWebhookEventStatusesWithLatestLog",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "webhookId": webhook_id,
            },
            query={"page": page, "size": size, "statuses": statuses},
        )

    @server.tool(name="clockify_webhooks_list_for_addon", annotations=READ_ANNOTATIONS)
    async def clockify_webhooks_list_for_addon(
        addon_id: str, workspace_id: str | None = None
    ) -> ReadResult:
        """List the webhooks that one addon registered on the workspace."""
        return await raw_read(
            client,
            "getAddonWebhooksOnWorkspace",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "addonId": addon_id,
            },
        )

    @server.tool(name="clockify_webhooks_search_logs", annotations=READ_ANNOTATIONS)
    async def clockify_webhooks_search_logs(
        webhook_id: str,
        workspace_id: str | None = None,
        body: dict[str, Any] | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> ReadResult:
        """Search a webhook's delivery logs (non-mutating POST). `body` is a
        WebhookLogsRequest filter; pagination goes through the page/size query
        parameters (page default 0)."""
        return await raw_read(
            client,
            "getWebhookLogs",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "webhookId": webhook_id,
            },
            query={"page": page, "size": size},
            body=body,
        )
