"""Public-method wiring: time_off_balance_assignments (4 operations)."""

from clockify.models import BalanceAssignmentV1Dto

from ._harness import assert_wired, make_client

COVERED = {
    "createBalanceAssignment",
    "deleteBalanceAssignment",
    "getBalanceAssignmentsForUserAndPolicy",
    "updateBalanceAssignment",
}

ASSIGNMENT_JSON = {"id": "ba1", "userId": "u1", "policyId": "pol1"}


async def test_create() -> None:
    client, capture = make_client(status=201, content=b"")
    result = await client.time_off_balance_assignments.create(
        {"balance": 2.0, "policyId": "pol1", "userIds": ["u1"]}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_off_balance_assignments",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/balance/assignment",
    )
    assert capture.sent_json() == {"balance": 2.0, "policyId": "pol1", "userIds": ["u1"]}
    assert result is None


async def test_delete_sends_required_body() -> None:
    client, capture = make_client(status=200, content=b"")
    result = await client.time_off_balance_assignments.delete(
        "ba1", "u1", "pol1", {"note": "cleanup"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_off_balance_assignments",
        method="delete",
        url=(
            "https://api.clockify.me/api/v1/workspaces/w1/time-off/balance"
            "/assignment/ba1/user/u1/policy/pol1"
        ),
    )
    assert capture.request.method == "DELETE"
    assert capture.sent_json() == {"note": "cleanup"}
    assert result is None


async def test_get_for_user_and_policy() -> None:
    client, capture = make_client(json=[ASSIGNMENT_JSON])
    assignments = await client.time_off_balance_assignments.get_for_user_and_policy(
        "u1", "pol1", workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_off_balance_assignments",
        method="get_for_user_and_policy",
        url=(
            "https://api.clockify.me/api/v1/workspaces/w1/time-off/balance"
            "/assignment/user/u1/policy/pol1"
        ),
    )
    assert isinstance(assignments[0], BalanceAssignmentV1Dto)


async def test_get_for_user_and_policy_default_workspace() -> None:
    client, capture = make_client(json=[])
    await client.time_off_balance_assignments.get_for_user_and_policy("u1", "pol1")
    assert "/workspaces/w-default/time-off/balance/assignment" in str(capture.request.url)


async def test_update() -> None:
    client, capture = make_client(status=204, content=b"")
    result = await client.time_off_balance_assignments.update(
        "ba1", "u1", "pol1", {"balanceChange": -4.0}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_off_balance_assignments",
        method="update",
        url=(
            "https://api.clockify.me/api/v1/workspaces/w1/time-off/balance"
            "/assignment/ba1/user/u1/policy/pol1"
        ),
    )
    assert capture.sent_json() == {"balanceChange": -4.0}
    assert result is None
