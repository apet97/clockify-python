"""Public-method wiring: scheduling (11 operations)."""

from clockify.models import (
    AssignmentListItem,
    ProjectAssignmentsTotal,
    SchedulingAssignment,
    UserCapacityTotal,
)

from ._harness import assert_wired, make_client

COVERED = {
    "changeRecurringPeriod",
    "copyScheduledAssignment",
    "createRecurringAssignment",
    "deleteRecurringAssignment",
    "getUsersCapacityTotals",
    "getScheduledAssignmentsOnProject",
    "getUserCapacityTotal",
    "getAllSchedulingAssignments",
    "getScheduledAssignmentsPerProject",
    "publishAssignments",
    "updateRecurringAssignment",
}

ASSIGNMENT_JSON = {"id": "a1", "userId": "u1", "projectId": "p1"}
START = "2026-01-01T00:00:00Z"
END = "2026-01-07T00:00:00Z"


async def test_change_recurring_period() -> None:
    client, capture = make_client(json=[ASSIGNMENT_JSON])
    result = await client.scheduling.change_recurring_period(
        "a1", {"repeat": True, "weeks": 4}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="change_recurring_period",
        url="https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/series/a1",
    )
    assert capture.sent_json() == {"repeat": True, "weeks": 4}
    assert isinstance(result[0], SchedulingAssignment)


async def test_copy_assignment() -> None:
    client, capture = make_client(status=201, json=[ASSIGNMENT_JSON])
    result = await client.scheduling.copy_assignment(
        "a1", {"seriesUpdateOption": "THIS_ONE", "userId": "u2"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="copy_assignment",
        url="https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/a1/copy",
    )
    assert capture.sent_json() == {"seriesUpdateOption": "THIS_ONE", "userId": "u2"}
    assert isinstance(result[0], SchedulingAssignment)


async def test_create_recurring() -> None:
    client, capture = make_client(status=201, json=[ASSIGNMENT_JSON])
    result = await client.scheduling.create_recurring(
        {
            "start": START,
            "end": END,
            "hoursPerDay": 8,
            "projectId": "p1",
            "userId": "u1",
        },
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="create_recurring",
        url="https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/recurring",
    )
    sent = capture.sent_json()
    assert sent["projectId"] == "p1"
    assert sent["userId"] == "u1"
    assert result[0].id == "a1"


async def test_delete_recurring_query() -> None:
    client, capture = make_client(json=[ASSIGNMENT_JSON])
    await client.scheduling.delete_recurring("a1", workspace_id="w1", series_update_option="ALL")
    assert_wired(
        capture,
        resource="scheduling",
        method="delete_recurring",
        url="https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/recurring/a1",
        query={"seriesUpdateOption": ["ALL"]},
    )


async def test_get_filtered_user_capacity() -> None:
    client, capture = make_client(json=[{"userId": "u1"}])
    result = await client.scheduling.get_filtered_user_capacity(
        {"start": START, "end": END}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="get_filtered_user_capacity",
        url=(
            "https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/user-filter/totals"
        ),
    )
    sent = capture.sent_json()
    assert sent["start"] == START
    assert sent["end"] == END
    assert isinstance(result[0], UserCapacityTotal)


async def test_get_project_totals_query() -> None:
    client, capture = make_client(json={"projectId": "p1"})
    result = await client.scheduling.get_project_totals(
        "p1", workspace_id="w1", start=START, end=END
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="get_project_totals",
        url=(
            "https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/projects/totals/p1"
        ),
        query={"start": [START], "end": [END]},
    )
    assert isinstance(result, ProjectAssignmentsTotal)


async def test_get_user_capacity_query() -> None:
    client, capture = make_client(json={"userId": "u1"})
    result = await client.scheduling.get_user_capacity(
        "u1", workspace_id="w1", page=1, page_size=50, start=START, end=END
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="get_user_capacity",
        url="https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/users/u1/totals",
        query={
            "page": ["1"],
            "page-size": ["50"],
            "start": [START],
            "end": [END],
        },
    )
    assert isinstance(result, UserCapacityTotal)


async def test_list_assignments_query_and_default_workspace() -> None:
    client, capture = make_client(json=[{"id": "a1"}])
    result = await client.scheduling.list_assignments(
        name="alice",
        start=START,
        end=END,
        sort_column="NAME",
        sort_order="ASCENDING",
        page=2,
        page_size=10,
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="list_assignments",
        url=("https://api.clockify.me/api/v1/workspaces/w-default/scheduling/assignments/all"),
        query={
            "name": ["alice"],
            "start": [START],
            "end": [END],
            "sort-column": ["NAME"],
            "sort-order": ["ASCENDING"],
            "page": ["2"],
            "page-size": ["10"],
        },
    )
    assert isinstance(result[0], AssignmentListItem)


async def test_list_project_totals() -> None:
    client, capture = make_client(json=[{"projectId": "p1"}])
    result = await client.scheduling.list_project_totals(
        {"start": START, "end": END}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="list_project_totals",
        url=("https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/projects/totals"),
    )
    sent = capture.sent_json()
    assert sent["start"] == START
    assert sent["end"] == END
    assert isinstance(result[0], ProjectAssignmentsTotal)


async def test_publish_assignments_returns_none() -> None:
    client, capture = make_client(content=b"")
    result = await client.scheduling.publish_assignments(
        {"start": START, "end": END}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="publish_assignments",
        url="https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/publish",
    )
    sent = capture.sent_json()
    assert sent["start"] == START
    assert sent["end"] == END
    assert result is None


async def test_update_recurring() -> None:
    client, capture = make_client(json=[ASSIGNMENT_JSON])
    result = await client.scheduling.update_recurring(
        "a1", {"start": START, "end": END}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="scheduling",
        method="update_recurring",
        url="https://api.clockify.me/api/v1/workspaces/w1/scheduling/assignments/recurring/a1",
    )
    sent = capture.sent_json()
    assert sent["start"] == START
    assert sent["end"] == END
    assert isinstance(result[0], SchedulingAssignment)
