"""Public-method wiring: webhooks (9 operations)."""

from clockify.models import (
    WebhookCollectionDtoV1,
    WebhookDtoV1,
    WebhookEventStatusWithLatestLogDtoV1,
    WebhookLogDtoV1,
    WebhooksWebhook2,
)

from ._harness import assert_wired, make_client

COVERED = {
    "createWebhook",
    "deleteWebhook",
    "getWebhookById",
    "getWebhooksOnWorkspace",
    "getWebhookEventStatusesWithLatestLog",
    "getAddonWebhooksOnWorkspace",
    "patchWorkspacesWorkspaceIdWebhooksWebhookIdToken",
    "getWebhookLogs",
    "updateWebhook",
}

WEBHOOK_JSON = {"id": "wh1", "name": "hook", "url": "https://example.com/hook"}
CREATE_BODY = {
    "name": "hook",
    "triggerSource": [],
    "triggerSourceType": "WORKSPACE_ID",
    "url": "https://example.com/hook",
    "webhookEvent": "TIMER_STOPPED",
}


async def test_create() -> None:
    client, capture = make_client(status=201, json=WEBHOOK_JSON)
    webhook = await client.webhooks.create(CREATE_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="webhooks",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/webhooks",
    )
    assert capture.sent_json() == CREATE_BODY
    assert isinstance(webhook, WebhookDtoV1)


async def test_delete_returns_none() -> None:
    client, capture = make_client(status=204)
    result = await client.webhooks.delete("wh1", workspace_id="w1")
    assert_wired(
        capture,
        resource="webhooks",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/webhooks/wh1",
    )
    assert result is None


async def test_get() -> None:
    client, capture = make_client(json=WEBHOOK_JSON)
    webhook = await client.webhooks.get("wh1", workspace_id="w1")
    assert_wired(
        capture,
        resource="webhooks",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/webhooks/wh1",
    )
    assert isinstance(webhook, WebhookDtoV1)


async def test_list_returns_envelope() -> None:
    client, capture = make_client(json={"webhooks": [WEBHOOK_JSON], "workspaceId": "w1"})
    collection = await client.webhooks.list(workspace_id="w1", type="ADDON")
    assert_wired(
        capture,
        resource="webhooks",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/webhooks",
        query={"type": ["ADDON"]},
    )
    assert isinstance(collection, WebhookCollectionDtoV1)


async def test_list_default_workspace() -> None:
    client, capture = make_client(json={"webhooks": []})
    await client.webhooks.list()
    assert "/workspaces/w-default/webhooks" in str(capture.request.url)


async def test_list_event_statuses_query_wire_names() -> None:
    client, capture = make_client(json=[{"eventType": "TIMER_STOPPED"}])
    statuses = await client.webhooks.list_event_statuses(
        "wh1", workspace_id="w1", page=0, size=20, statuses="FAILED"
    )
    assert_wired(
        capture,
        resource="webhooks",
        method="list_event_statuses",
        url="https://api.clockify.me/api/v1/workspaces/w1/webhooks/wh1/statuses",
        query={"page": ["0"], "size": ["20"], "statuses": ["FAILED"]},
    )
    assert isinstance(statuses[0], WebhookEventStatusWithLatestLogDtoV1)


async def test_list_for_addon_returns_envelope() -> None:
    client, capture = make_client(json={"webhooks": [WEBHOOK_JSON]})
    collection = await client.webhooks.list_for_addon("ad1", workspace_id="w1")
    assert_wired(
        capture,
        resource="webhooks",
        method="list_for_addon",
        url="https://api.clockify.me/api/v1/workspaces/w1/addons/ad1/webhooks",
    )
    assert isinstance(collection, WebhookCollectionDtoV1)


async def test_rotate_token_bodyless_patch() -> None:
    client, capture = make_client(json={"id": "wh1", "authToken": "t2"})
    webhook = await client.webhooks.rotate_token("wh1", workspace_id="w1")
    assert_wired(
        capture,
        resource="webhooks",
        method="rotate_token",
        url="https://api.clockify.me/api/v1/workspaces/w1/webhooks/wh1/token",
    )
    assert not capture.request.content
    assert isinstance(webhook, WebhooksWebhook2)


async def test_search_logs_is_post_read_with_query_pagination() -> None:
    client, capture = make_client(json=[{"id": "log1"}])
    logs = await client.webhooks.search_logs(
        "wh1", {"status": "FAILED"}, workspace_id="w1", page=0, size=50
    )
    assert_wired(
        capture,
        resource="webhooks",
        method="search_logs",
        url="https://api.clockify.me/api/v1/workspaces/w1/webhooks/wh1/logs",
        query={"page": ["0"], "size": ["50"]},
    )
    assert capture.request.method == "POST"
    assert capture.sent_json() == {"status": "FAILED"}
    assert isinstance(logs[0], WebhookLogDtoV1)


async def test_update_sends_exact_body() -> None:
    client, capture = make_client(json=WEBHOOK_JSON)
    await client.webhooks.update("wh1", CREATE_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="webhooks",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/webhooks/wh1",
    )
    assert capture.sent_json() == CREATE_BODY
