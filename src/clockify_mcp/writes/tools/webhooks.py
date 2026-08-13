# pyright: reportUnusedFunction=false
"""Guarded write tools: webhooks."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import WebhookRequest
from clockify_mcp.webhook_url import assert_safe_webhook_url
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def _redact_token(result: WriteResult) -> WriteResult:
    """Never let the webhook authToken into the transcript."""
    if isinstance(result.data, dict) and "authToken" in result.data:
        result.data = {**result.data, "authToken": "[redacted]"}
    return result


def register(server: MCPServer, deps: WriteDeps) -> None:

    create = GuardedOp(
        deps,
        tool_name="clockify_webhooks_create",
        title="Create webhook",
        operation_id="createWebhook",
        body_model=WebhookRequest,
    )

    async def prepare_create(
        body: WebhookRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        assert_safe_webhook_url(body.url)
        return await create.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": create.workspace(workspace_id)},
            body=body,
        )

    def ask_create(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_webhooks_create", annotations=tool_annotations("clockify_webhooks_create")
    )
    async def clockify_webhooks_create(
        body: WebhookRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a webhook. The returned authToken is redacted from the receipt."""
        return _redact_token(await create.run(prepared, approval))

    update = GuardedOp(
        deps,
        tool_name="clockify_webhooks_update",
        title="Update webhook",
        operation_id="updateWebhook",
        body_model=WebhookRequest,
    )

    async def prepare_update(
        webhook_id: str, body: WebhookRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        assert_safe_webhook_url(body.url)
        return await update.prepare(
            arguments={"webhook_id": webhook_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id), "webhookId": webhook_id},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_webhooks_update", annotations=tool_annotations("clockify_webhooks_update")
    )
    async def clockify_webhooks_update(
        webhook_id: str,
        body: WebhookRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace a webhook (PUT). The returned authToken is redacted from the receipt."""
        return _redact_token(await update.run(prepared, approval))

    rotate_token = GuardedOp(
        deps,
        tool_name="clockify_webhooks_rotate_token",
        title="Rotate webhook token",
        operation_id="patchWorkspacesWorkspaceIdWebhooksWebhookIdToken",
    )

    async def prepare_rotate_token(
        webhook_id: str, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await rotate_token.prepare(
            arguments={"webhook_id": webhook_id, "workspace_id": workspace_id},
            path_args={
                "workspaceId": rotate_token.workspace(workspace_id),
                "webhookId": webhook_id,
            },
        )

    def ask_rotate_token(
        prepared: Annotated[PreparedWrite, Resolve(prepare_rotate_token)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_webhooks_rotate_token",
        annotations=tool_annotations("clockify_webhooks_rotate_token"),
    )
    async def clockify_webhooks_rotate_token(
        webhook_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_rotate_token)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_rotate_token)],
    ) -> WriteResult:
        """Generate a new webhook token. The token is redacted from the receipt."""
        return _redact_token(await rotate_token.run(prepared, approval))

    delete = GuardedOp(
        deps,
        tool_name="clockify_webhooks_delete",
        title="Delete webhook",
        operation_id="deleteWebhook",
    )

    async def prepare_delete(webhook_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"webhook_id": webhook_id, "workspace_id": workspace_id},
            path_args={"workspaceId": delete.workspace(workspace_id), "webhookId": webhook_id},
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_webhooks_delete", annotations=tool_annotations("clockify_webhooks_delete")
    )
    async def clockify_webhooks_delete(
        webhook_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a webhook. NOT reversible."""
        return await delete.run(prepared, approval)
