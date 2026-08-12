"""Public-method wiring: time_off_balances (3 operations)."""

from clockify.models import BalanceListResponse

from ._harness import assert_wired, make_client

COVERED = {
    "getBalancesForPolicy",
    "getBalanceForUser",
    "updateBalance",
}

BALANCES_JSON = {"balances": [{"id": "b1", "userId": "u1", "policyId": "pol1"}], "count": 1}


async def test_list_for_policy_returns_envelope() -> None:
    client, capture = make_client(json=BALANCES_JSON)
    result = await client.time_off_balances.list_for_policy(
        "pol1", workspace_id="w1", page=1, page_size=50, sort="USER", sort_order="ASCENDING"
    )
    assert_wired(
        capture,
        resource="time_off_balances",
        method="list_for_policy",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/balance/policy/pol1",
        query={
            "page": ["1"],
            "page-size": ["50"],
            "sort": ["USER"],
            "sort-order": ["ASCENDING"],
        },
    )
    assert isinstance(result, BalanceListResponse)


async def test_list_for_user_returns_envelope() -> None:
    client, capture = make_client(json=BALANCES_JSON)
    result = await client.time_off_balances.list_for_user(
        "u1", workspace_id="w1", page=2, page_size=10, sort="POLICY", sort_order="DESCENDING"
    )
    assert_wired(
        capture,
        resource="time_off_balances",
        method="list_for_user",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/balance/user/u1",
        query={
            "page": ["2"],
            "page-size": ["10"],
            "sort": ["POLICY"],
            "sort-order": ["DESCENDING"],
        },
    )
    assert isinstance(result, BalanceListResponse)


async def test_list_for_user_default_workspace() -> None:
    client, capture = make_client(json=BALANCES_JSON)
    await client.time_off_balances.list_for_user("u1")
    assert "/workspaces/w-default/time-off/balance/user/u1" in str(capture.request.url)


async def test_update_for_policy() -> None:
    client, capture = make_client(status=204, content=b"")
    result = await client.time_off_balances.update_for_policy(
        "pol1", {"note": "adjust", "userIds": ["u1"], "value": 3.0}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_off_balances",
        method="update_for_policy",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/balance/policy/pol1",
    )
    assert capture.sent_json() == {"note": "adjust", "userIds": ["u1"], "value": 3.0}
    assert result is None
