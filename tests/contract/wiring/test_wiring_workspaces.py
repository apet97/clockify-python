"""Public-method wiring: workspaces (5 operations)."""

from clockify.models import Workspace

from ._harness import assert_wired, make_client

COVERED = {
    "addWorkspace",
    "getWorkspaceInfo",
    "getAllMyWorkspaces",
    "updateWorkspaceBillableRate",
    "updateWorkspaceCostRate",
}

WORKSPACE_JSON = {"id": "w1", "name": "Acme"}


async def test_create_has_no_workspace_segment() -> None:
    client, capture = make_client(status=201, json=WORKSPACE_JSON)
    workspace = await client.workspaces.create({"name": "Acme", "organizationId": "org1"})
    assert_wired(
        capture,
        resource="workspaces",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces",
    )
    assert capture.sent_json() == {"name": "Acme", "organizationId": "org1"}
    assert isinstance(workspace, Workspace)


async def test_get() -> None:
    client, capture = make_client(json=WORKSPACE_JSON)
    workspace = await client.workspaces.get(workspace_id="w1")
    assert_wired(
        capture,
        resource="workspaces",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1",
    )
    assert isinstance(workspace, Workspace)


async def test_get_default_workspace() -> None:
    client, capture = make_client(json=WORKSPACE_JSON)
    await client.workspaces.get()
    assert str(capture.request.url).endswith("/workspaces/w-default")


async def test_list_roles_repeated_key() -> None:
    client, capture = make_client(json=[WORKSPACE_JSON])
    workspaces = await client.workspaces.list(roles=["WORKSPACE_ADMIN", "OWNER"])
    assert_wired(
        capture,
        resource="workspaces",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces",
        query={"roles": ["WORKSPACE_ADMIN", "OWNER"]},
    )
    assert isinstance(workspaces[0], Workspace)


async def test_update_billable_rate() -> None:
    client, capture = make_client(json=WORKSPACE_JSON)
    workspace = await client.workspaces.update_billable_rate(
        {"amount": 10000, "currency": "USD"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="workspaces",
        method="update_billable_rate",
        url="https://api.clockify.me/api/v1/workspaces/w1/hourly-rate",
    )
    assert capture.sent_json() == {"amount": 10000, "currency": "USD"}
    assert isinstance(workspace, Workspace)


async def test_update_cost_rate() -> None:
    client, capture = make_client(json=WORKSPACE_JSON)
    workspace = await client.workspaces.update_cost_rate({"amount": 5000}, workspace_id="w1")
    assert_wired(
        capture,
        resource="workspaces",
        method="update_cost_rate",
        url="https://api.clockify.me/api/v1/workspaces/w1/cost-rate",
    )
    assert capture.sent_json() == {"amount": 5000}
    assert isinstance(workspace, Workspace)
