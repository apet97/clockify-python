"""Public-method wiring: approvals (8 operations)."""

from clockify.models import (
    ApprovalRequestDtoV1,
    ApprovalRequestListItem,
    SubmitApprovalRequestRequest,
    UpdateApprovalRequestRequest,
)

from ._harness import assert_wired, make_client

COVERED = {
    "getApprovalRequests",
    "resubmitEntriesForApproval",
    "resubmitEntriesForApprovalForUser",
    "submitApprovalRequest",
    "submitApprovalRequestForUser",
    "createApprovalForOtherWithType",
    "createApprrovalRequest_1",
    "updateApprovalRequest",
}

APPROVAL_JSON = {"id": "ar1", "workspaceId": "w1", "type": "TIMESHEET"}
LIST_ITEM_JSON = {"approvalRequest": APPROVAL_JSON, "trackedTime": "PT8H"}
SUBMIT_BODY = {"period": "WEEKLY", "periodStart": "2026-08-03T00:00:00Z"}
NO_TYPE_BODY = {"periodStart": "2026-08-03T00:00:00Z"}


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[LIST_ITEM_JSON])
    items = await client.approvals.list(
        workspace_id="w1",
        status="PENDING",
        sort_column="START",
        types=["TIMESHEET", "EXPENSE"],
        sort_order="ASCENDING",
        page=2,
        page_size=25,
    )
    assert_wired(
        capture,
        resource="approvals",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/approval-requests",
        query={
            "status": ["PENDING"],
            "sort-column": ["START"],
            "types": ["TIMESHEET", "EXPENSE"],
            "sort-order": ["ASCENDING"],
            "page": ["2"],
            "page-size": ["25"],
        },
    )
    assert isinstance(items[0], ApprovalRequestListItem)
    assert items[0].approval_request is not None
    assert items[0].approval_request.id == "ar1"


async def test_list_default_workspace() -> None:
    client, capture = make_client(json=[])
    await client.approvals.list()
    assert "/workspaces/w-default/approval-requests" in str(capture.request.url)


async def test_resubmit() -> None:
    client, capture = make_client(json=APPROVAL_JSON)
    result = await client.approvals.resubmit(
        SubmitApprovalRequestRequest(period="WEEKLY", periodStart="2026-08-03T00:00:00Z"),
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="approvals",
        method="resubmit",
        url=(
            "https://api.clockify.me/api/v1/workspaces/w1/approval-requests/"
            "resubmit-entries-for-approval"
        ),
    )
    assert capture.sent_json() == SUBMIT_BODY
    assert isinstance(result, ApprovalRequestDtoV1)


async def test_resubmit_for_user() -> None:
    client, capture = make_client(json=APPROVAL_JSON)
    await client.approvals.resubmit_for_user("u1", SUBMIT_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="approvals",
        method="resubmit_for_user",
        url=(
            "https://api.clockify.me/api/v1/workspaces/w1/approval-requests/users/u1/"
            "resubmit-entries-for-approval"
        ),
    )
    assert capture.sent_json() == SUBMIT_BODY


async def test_submit() -> None:
    client, capture = make_client(status=201, json=APPROVAL_JSON)
    result = await client.approvals.submit(SUBMIT_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="approvals",
        method="submit",
        url="https://api.clockify.me/api/v1/workspaces/w1/approval-requests",
    )
    assert capture.sent_json() == SUBMIT_BODY
    assert result.workspace_id == "w1"


async def test_submit_for_user() -> None:
    client, capture = make_client(status=201, json=APPROVAL_JSON)
    await client.approvals.submit_for_user("u1", SUBMIT_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="approvals",
        method="submit_for_user",
        url="https://api.clockify.me/api/v1/workspaces/w1/approval-requests/users/u1",
    )
    assert capture.sent_json() == SUBMIT_BODY


async def test_submit_for_user_with_type() -> None:
    client, capture = make_client(status=201, json=APPROVAL_JSON)
    result = await client.approvals.submit_for_user_with_type(
        "u1", "TIMESHEET", NO_TYPE_BODY, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="approvals",
        method="submit_for_user_with_type",
        url="https://api.clockify.me/api/v1/workspaces/w1/approval-requests/users/u1/TIMESHEET",
    )
    assert capture.sent_json() == NO_TYPE_BODY
    assert isinstance(result, ApprovalRequestDtoV1)


async def test_submit_with_type() -> None:
    client, capture = make_client(status=201, json=APPROVAL_JSON)
    await client.approvals.submit_with_type("TIMESHEET", NO_TYPE_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="approvals",
        method="submit_with_type",
        url="https://api.clockify.me/api/v1/workspaces/w1/approval-requests/TIMESHEET",
    )
    assert capture.sent_json() == NO_TYPE_BODY


async def test_update_status() -> None:
    client, capture = make_client(json=APPROVAL_JSON)
    result = await client.approvals.update_status(
        "ar1", UpdateApprovalRequestRequest(state="APPROVED"), workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="approvals",
        method="update_status",
        url="https://api.clockify.me/api/v1/workspaces/w1/approval-requests/ar1",
    )
    assert capture.sent_json() == {"state": "APPROVED"}
    assert isinstance(result, ApprovalRequestDtoV1)
