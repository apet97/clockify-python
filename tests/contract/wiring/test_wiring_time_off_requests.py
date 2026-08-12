"""Public-method wiring: time_off_requests (5 operations)."""

from clockify.models import (
    TimeOffRequestDto,
    TimeOffRequestFullV1Dto,
    TimeOffRequestsResponse,
)

from ._harness import assert_wired, make_client

COVERED = {
    "getAllTimeOffRequestsOnWorkspace",
    "createTimeOffRequest",
    "createTimeOffRequestForUser",
    "changeTimeOffRequestStatus",
    "deleteTimeOffRequest",
}

REQUEST_JSON = {"id": "r1", "policyId": "p1", "workspaceId": "w1"}
SUBMIT_BODY = {"timeOffPeriod": {"period": {"start": "2026-08-10", "days": 2}}}


async def test_list_is_post_read() -> None:
    client, capture = make_client(json={"count": 1, "requests": [REQUEST_JSON]})
    result = await client.time_off_requests.list({"statuses": ["PENDING"]}, workspace_id="w1")
    assert_wired(
        capture,
        resource="time_off_requests",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/requests",
    )
    assert capture.request.method == "POST"
    assert capture.sent_json() == {"statuses": ["PENDING"]}
    assert isinstance(result, TimeOffRequestsResponse)


async def test_list_default_workspace() -> None:
    client, capture = make_client(json={})
    await client.time_off_requests.list({})
    assert "/workspaces/w-default/time-off/requests" in str(capture.request.url)


async def test_submit() -> None:
    client, capture = make_client(status=201, json=REQUEST_JSON)
    result = await client.time_off_requests.submit("p1", SUBMIT_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="time_off_requests",
        method="submit",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies/p1/requests",
    )
    assert capture.sent_json() == SUBMIT_BODY
    assert isinstance(result, TimeOffRequestFullV1Dto)


async def test_submit_for_user() -> None:
    client, capture = make_client(status=201, json=REQUEST_JSON)
    result = await client.time_off_requests.submit_for_user(
        "p1", "u1", SUBMIT_BODY, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_off_requests",
        method="submit_for_user",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies/p1/users/u1/requests",
    )
    assert capture.sent_json() == SUBMIT_BODY
    assert isinstance(result, TimeOffRequestFullV1Dto)


async def test_update_status() -> None:
    client, capture = make_client(json=REQUEST_JSON)
    result = await client.time_off_requests.update_status(
        "p1", "r1", {"status": "APPROVED"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_off_requests",
        method="update_status",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies/p1/requests/r1",
    )
    assert capture.sent_json() == {"status": "APPROVED"}
    assert isinstance(result, TimeOffRequestDto)


async def test_withdraw() -> None:
    client, capture = make_client(json=REQUEST_JSON)
    result = await client.time_off_requests.withdraw("p1", "r1", workspace_id="w1")
    assert_wired(
        capture,
        resource="time_off_requests",
        method="withdraw",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-off/policies/p1/requests/r1",
    )
    assert isinstance(result, TimeOffRequestDto)
