"""Public-method wiring: time_entries (13 operations)."""

import pydantic
import pytest

from clockify.errors import ClockifyConfigurationError
from clockify.models import (
    GetTimeEntriesByIdsRequest,
    TimeEntriesTimeEntry,
    TimeEntry,
    TimeEntryDtoImplV1,
    TimeEntryWithRatesDtoV1,
)

from ._harness import assert_wired, make_client

COVERED = {
    "putWorkspacesWorkspaceIdUserUserIdTimeEntries",
    "postWorkspacesWorkspaceIdTimeEntries",
    "postWorkspacesWorkspaceIdUserUserIdTimeEntries",
    "deleteWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
    "deleteMany",
    "postWorkspacesWorkspaceIdUserUserIdTimeEntriesTimeEntryIdDuplicate",
    "getWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
    "getMultipleTimeEntries",
    "getWorkspacesWorkspaceIdUserUserIdTimeEntries",
    "getWorkspacesWorkspaceIdTimeEntriesStatusInProgress",
    "patchWorkspacesWorkspaceIdTimeEntriesInvoiced",
    "patchWorkspacesWorkspaceIdUserUserIdTimeEntries",
    "putWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
}

# TimeEntriesTimeEntry / TimeEntryDtoImplV1 / TimeEntryWithRatesDtoV1 have no
# required fields; TimeEntry requires the full core set.
ENTRY_JSON = {"id": "te1", "description": "work"}
FULL_ENTRY_JSON = {
    "id": "te1",
    "description": "work",
    "billable": False,
    "isLocked": False,
    "timeInterval": {},
    "type": "REGULAR",
    "userId": "u1",
    "workspaceId": "w1",
}


async def test_bulk_update_for_user() -> None:
    client, capture = make_client(json=[ENTRY_JSON])
    entries = await client.time_entries.bulk_update_for_user(
        "u1",
        [{"id": "te1", "start": "2026-01-01T00:00:00Z", "end": "2026-01-01T01:00:00Z"}],
        workspace_id="w1",
        hydrated=True,
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="bulk_update_for_user",
        url="https://api.clockify.me/api/v1/workspaces/w1/user/u1/time-entries",
        query={"hydrated": ["true"]},
    )
    assert capture.sent_json() == [
        {"id": "te1", "start": "2026-01-01T00:00:00Z", "end": "2026-01-01T01:00:00Z"}
    ]
    assert isinstance(entries[0], TimeEntriesTimeEntry)


async def test_create() -> None:
    client, capture = make_client(status=201, json=ENTRY_JSON)
    entry = await client.time_entries.create(
        {"start": "2026-01-01T00:00:00Z", "description": "work"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-entries",
    )
    assert capture.sent_json() == {"start": "2026-01-01T00:00:00Z", "description": "work"}
    assert isinstance(entry, TimeEntriesTimeEntry)


async def test_create_default_workspace() -> None:
    client, capture = make_client(status=201, json=ENTRY_JSON)
    await client.time_entries.create({"start": "2026-01-01T00:00:00Z"})
    assert "/workspaces/w-default/time-entries" in str(capture.request.url)


async def test_create_for_user() -> None:
    client, capture = make_client(status=201, json=FULL_ENTRY_JSON)
    entry = await client.time_entries.create_for_user(
        "u1",
        {"start": "2026-01-01T00:00:00Z"},
        workspace_id="w1",
        from_entry="te0",
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="create_for_user",
        url="https://api.clockify.me/api/v1/workspaces/w1/user/u1/time-entries",
        query={"from-entry": ["te0"]},
    )
    assert capture.sent_json() == {"start": "2026-01-01T00:00:00Z"}
    assert isinstance(entry, TimeEntry)


async def test_delete() -> None:
    client, capture = make_client(status=204, content=b"")
    result = await client.time_entries.delete("te1", workspace_id="w1")
    assert_wired(
        capture,
        resource="time_entries",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-entries/te1",
    )
    assert result is None


async def test_delete_all_for_user() -> None:
    client, capture = make_client(json=[ENTRY_JSON])
    entries = await client.time_entries.delete_all_for_user(
        "u1", workspace_id="w1", time_entry_ids=["te1", "te2"]
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="delete_all_for_user",
        url="https://api.clockify.me/api/v1/workspaces/w1/user/u1/time-entries",
        query={"time-entry-ids": ["te1", "te2"]},
    )
    assert isinstance(entries[0], TimeEntryDtoImplV1)


async def test_delete_all_rejects_empty_ids_before_transport() -> None:
    client, capture = make_client(json=[])

    with pytest.raises(
        ClockifyConfigurationError, match="required query parameter 'time_entry_ids'"
    ):
        await client.time_entries.delete_all_for_user("u1", workspace_id="w1", time_entry_ids=[])

    assert capture.requests == []


async def test_duplicate() -> None:
    client, capture = make_client(status=201, json=ENTRY_JSON)
    entry = await client.time_entries.duplicate("u1", "te1", workspace_id="w1")
    assert_wired(
        capture,
        resource="time_entries",
        method="duplicate",
        url="https://api.clockify.me/api/v1/workspaces/w1/user/u1/time-entries/te1/duplicate",
    )
    assert isinstance(entry, TimeEntriesTimeEntry)


async def test_get() -> None:
    client, capture = make_client(json=FULL_ENTRY_JSON)
    entry = await client.time_entries.get(
        "te1", workspace_id="w1", hydrated=True, consider_duration_format=False
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-entries/te1",
        query={"hydrated": ["true"], "consider-duration-format": ["false"]},
    )
    assert isinstance(entry, TimeEntry)


async def test_get_many_is_post_read() -> None:
    client, capture = make_client(json=[ENTRY_JSON])
    entries = await client.time_entries.get_many(
        GetTimeEntriesByIdsRequest(timeEntryIds=["te1", "te2"]), workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="get_many",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-entries/batch",
    )
    assert capture.request.method == "POST"
    assert capture.sent_json() == {"timeEntryIds": ["te1", "te2"]}
    assert isinstance(entries[0], TimeEntryWithRatesDtoV1)


async def test_list_for_user_query_wire_names() -> None:
    client, capture = make_client(json=[FULL_ENTRY_JSON])
    entries = await client.time_entries.list_for_user(
        "u1",
        workspace_id="w1",
        description="work",
        start="2026-01-01T00:00:00Z",
        end="2026-01-02T00:00:00Z",
        project="p1",
        task="tk1",
        tags=["t1", "t2"],
        project_required=True,
        task_required=False,
        hydrated=True,
        in_progress=False,
        get_week_before="2026-01-01T00:00:00Z",
        page=2,
        page_size=25,
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="list_for_user",
        url="https://api.clockify.me/api/v1/workspaces/w1/user/u1/time-entries",
        query={
            "description": ["work"],
            "start": ["2026-01-01T00:00:00Z"],
            "end": ["2026-01-02T00:00:00Z"],
            "project": ["p1"],
            "task": ["tk1"],
            "tags": ["t1", "t2"],
            "project-required": ["true"],
            "task-required": ["false"],
            "hydrated": ["true"],
            "in-progress": ["false"],
            "get-week-before": ["2026-01-01T00:00:00Z"],
            "page": ["2"],
            "page-size": ["25"],
        },
    )
    assert isinstance(entries[0], TimeEntry)


async def test_list_in_progress() -> None:
    client, capture = make_client(json=[ENTRY_JSON])
    entries = await client.time_entries.list_in_progress(workspace_id="w1", page=1, page_size=10)
    assert_wired(
        capture,
        resource="time_entries",
        method="list_in_progress",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-entries/status/in-progress",
        query={"page": ["1"], "page-size": ["10"]},
    )
    assert isinstance(entries[0], TimeEntriesTimeEntry)


async def test_mark_invoiced() -> None:
    client, capture = make_client(status=204, content=b"")
    result = await client.time_entries.mark_invoiced(
        {"invoiced": True, "timeEntryIds": ["te1"]}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="mark_invoiced",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-entries/invoiced",
    )
    assert capture.sent_json() == {"invoiced": True, "timeEntryIds": ["te1"]}
    assert result is None


async def test_mark_invoiced_requires_ids_before_transport() -> None:
    client, capture = make_client(status=204, content=b"")

    with pytest.raises(pydantic.ValidationError):
        await client.time_entries.mark_invoiced({"invoiced": True}, workspace_id="w1")

    assert capture.requests == []


async def test_mark_invoiced_rejects_unknown_field_before_transport() -> None:
    client, capture = make_client(status=204, content=b"")

    with pytest.raises(pydantic.ValidationError):
        await client.time_entries.mark_invoiced(
            {"invoiced": True, "timeEntryIds": ["te1"], "invoice": False},
            workspace_id="w1",
        )

    assert capture.requests == []


async def test_stop_timer_for_user() -> None:
    client, capture = make_client(json=ENTRY_JSON)
    entry = await client.time_entries.stop_timer_for_user(
        "u1", {"end": "2026-01-01T01:00:00Z"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="stop_timer_for_user",
        url="https://api.clockify.me/api/v1/workspaces/w1/user/u1/time-entries",
    )
    assert capture.sent_json() == {"end": "2026-01-01T01:00:00Z"}
    assert isinstance(entry, TimeEntriesTimeEntry)


async def test_stop_timer_requires_end_before_transport() -> None:
    client, capture = make_client(json=ENTRY_JSON)

    with pytest.raises(pydantic.ValidationError):
        await client.time_entries.stop_timer_for_user("u1", {}, workspace_id="w1")

    assert capture.requests == []


async def test_stop_timer_rejects_unknown_field_before_transport() -> None:
    client, capture = make_client(json=ENTRY_JSON)

    with pytest.raises(pydantic.ValidationError):
        await client.time_entries.stop_timer_for_user(
            "u1",
            {"end": "2026-01-01T01:00:00Z", "ends": "2026-01-01T02:00:00Z"},
            workspace_id="w1",
        )

    assert capture.requests == []


async def test_update() -> None:
    client, capture = make_client(json=FULL_ENTRY_JSON)
    entry = await client.time_entries.update(
        "te1", {"start": "2026-01-01T00:00:00Z", "billable": True}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="time_entries",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/time-entries/te1",
    )
    assert capture.sent_json() == {"start": "2026-01-01T00:00:00Z", "billable": True}
    assert isinstance(entry, TimeEntry)
