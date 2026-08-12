"""Public-method wiring: time_off_policies (6 operations)."""

from clockify.models import Policy

from ._harness import assert_wired, make_client

COVERED = {
    "createTimeOffPolicy",
    "deleteTimeOffPolicy",
    "getTimeOffPolicy",
    "getTimeOffPolicies",
    "updateTimeOffPolicy",
    "changeTimeOffPolicyStatus",
}

POLICY_JSON = {"id": "p1", "name": "Vacation", "workspaceId": "w1"}

CREATE_BODY = {
    "name": "Vacation",
    "approve": {"requiresApproval": True},
}

UPDATE_BODY = {
    "name": "Vacation",
    "approve": {"requiresApproval": True},
    "allowHalfDay": False,
    "allowNegativeBalance": False,
    "archived": False,
    "everyoneIncludingNew": True,
    "hasExpiration": False,
    "users": {"contains": "CONTAINS", "ids": ["u1"], "status": "ACTIVE"},
    "userGroups": {"contains": "CONTAINS", "ids": [], "status": "ACTIVE"},
}


async def test_create() -> None:
    client, capture = make_client(status=201, json=POLICY_JSON)
    policy = await client.time_off_policies.create(CREATE_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="time_off_policies",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies",
    )
    assert capture.sent_json() == CREATE_BODY
    assert isinstance(policy, Policy)


async def test_delete_returns_none() -> None:
    client, capture = make_client(status=204)
    result = await client.time_off_policies.delete("p1", workspace_id="w1")
    assert_wired(
        capture,
        resource="time_off_policies",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies/p1",
    )
    assert result is None


async def test_get() -> None:
    client, capture = make_client(json=POLICY_JSON)
    policy = await client.time_off_policies.get("p1", workspace_id="w1")
    assert_wired(
        capture,
        resource="time_off_policies",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies/p1",
    )
    assert isinstance(policy, Policy)


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[POLICY_JSON])
    policies = await client.time_off_policies.list(
        workspace_id="w1",
        page=2,
        page_size=10,
        name="Vac",
        status="ACTIVE",
        sort_column="NAME",
        sort_order="ASCENDING",
    )
    assert_wired(
        capture,
        resource="time_off_policies",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies",
        query={
            "page": ["2"],
            "page-size": ["10"],
            "name": ["Vac"],
            "status": ["ACTIVE"],
            "sort-column": ["NAME"],
            "sort-order": ["ASCENDING"],
        },
    )
    assert isinstance(policies[0], Policy)


async def test_list_default_workspace() -> None:
    client, capture = make_client(json=[])
    await client.time_off_policies.list()
    assert "/workspaces/w-default/time-off/policies" in str(capture.request.url)


async def test_update_sends_exact_body() -> None:
    client, capture = make_client(json=POLICY_JSON)
    await client.time_off_policies.update("p1", UPDATE_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="time_off_policies",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies/p1",
    )
    assert capture.sent_json() == UPDATE_BODY


async def test_update_status() -> None:
    client, capture = make_client(json=POLICY_JSON)
    policy = await client.time_off_policies.update_status(
        "p1", {"status": "ARCHIVED"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_off_policies",
        method="update_status",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies/p1",
    )
    assert capture.sent_json() == {"status": "ARCHIVED"}
    assert isinstance(policy, Policy)
