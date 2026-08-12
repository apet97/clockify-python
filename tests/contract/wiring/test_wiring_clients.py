"""Public-method wiring: clients (5 operations)."""

from clockify.models import Client, ClientCreate

from ._harness import assert_wired, make_client

COVERED = {
    "postWorkspacesWorkspaceIdClients",
    "deleteWorkspacesWorkspaceIdClientsClientId",
    "getWorkspacesWorkspaceIdClientsClientId",
    "getWorkspacesWorkspaceIdClients",
    "putWorkspacesWorkspaceIdClientsClientId",
}

CLIENT_JSON = {"id": "c1", "name": "Acme", "workspaceId": "w1", "archived": False}


async def test_create() -> None:
    client, capture = make_client(status=201, json=CLIENT_JSON)
    result = await client.clients.create(ClientCreate(name="Acme"), workspace_id="w1")
    assert_wired(
        capture,
        resource="clients",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/clients",
    )
    assert capture.sent_json() == {"name": "Acme"}
    assert isinstance(result, Client)
    assert result.id == "c1"


async def test_create_accepts_mapping_and_default_workspace() -> None:
    client, capture = make_client(status=201, json=CLIENT_JSON)
    await client.clients.create({"name": "Acme"})
    assert "/workspaces/w-default/clients" in str(capture.request.url)


async def test_delete_returns_deleted_entity() -> None:
    client, capture = make_client(json=CLIENT_JSON)
    result = await client.clients.delete("c1", workspace_id="w1")
    assert_wired(
        capture,
        resource="clients",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/clients/c1",
    )
    assert result.name == "Acme"


async def test_get() -> None:
    client, capture = make_client(json=CLIENT_JSON)
    await client.clients.get("c1", workspace_id="w1")
    assert_wired(
        capture,
        resource="clients",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/clients/c1",
    )


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[CLIENT_JSON])
    clients = await client.clients.list(
        workspace_id="w1",
        name="Ac",
        archived=False,
        address="Main St",
        note="vip",
        sort_column="NAME",
        sort_order="ASCENDING",
        page=2,
        page_size=10,
    )
    assert_wired(
        capture,
        resource="clients",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/clients",
        query={
            "name": ["Ac"],
            "archived": ["false"],
            "address": ["Main St"],
            "note": ["vip"],
            "sort-column": ["NAME"],
            "sort-order": ["ASCENDING"],
            "page": ["2"],
            "page-size": ["10"],
        },
    )
    assert [c.id for c in clients] == ["c1"]


async def test_update_sends_exact_body_and_query() -> None:
    client, capture = make_client(json=CLIENT_JSON)
    await client.clients.update(
        "c1",
        {"name": "Acme", "archived": True, "ccEmails": ["a@b.c"]},
        workspace_id="w1",
        archive_projects=True,
        mark_tasks_as_done=False,
    )
    assert_wired(
        capture,
        resource="clients",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/clients/c1",
        query={"archive-projects": ["true"], "mark-tasks-as-done": ["false"]},
    )
    assert capture.sent_json() == {"name": "Acme", "archived": True, "ccEmails": ["a@b.c"]}
