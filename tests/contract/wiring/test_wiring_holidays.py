"""Public-method wiring: holidays (5 operations)."""

from clockify.models import HolidayDetailsDto, HolidayDto

from ._harness import assert_wired, make_client

COVERED = {
    "createHoliday",
    "deleteHoliday",
    "getWorkspaceHolidays",
    "getWorkspaceHolidaysInPeriod",
    "updateHoliday",
}

HOLIDAY_JSON = {
    "id": "h1",
    "name": "New Year",
    "workspaceId": "w1",
    "datePeriod": {"startDate": "2026-01-01", "endDate": "2026-01-01"},
}


async def test_create() -> None:
    client, capture = make_client(status=201, json=HOLIDAY_JSON)
    holiday = await client.holidays.create(
        {
            "name": "New Year",
            "datePeriod": {"startDate": "2026-01-01", "endDate": "2026-01-01"},
            "users": {"contains": "CONTAINS", "ids": ["u1"], "status": "ALL"},
        },
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="holidays",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/holidays",
    )
    assert capture.sent_json() == {
        "name": "New Year",
        "datePeriod": {"startDate": "2026-01-01", "endDate": "2026-01-01"},
        "users": {"contains": "CONTAINS", "ids": ["u1"], "status": "ALL"},
    }
    assert isinstance(holiday, HolidayDto)
    assert holiday.id == "h1"


async def test_delete_returns_details_dto() -> None:
    client, capture = make_client(json={**HOLIDAY_JSON, "userIds": ["u1"]})
    deleted = await client.holidays.delete("h1", workspace_id="w1")
    assert_wired(
        capture,
        resource="holidays",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/holidays/h1",
    )
    assert isinstance(deleted, HolidayDetailsDto)
    assert deleted.user_ids == ["u1"]


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[HOLIDAY_JSON])
    holidays = await client.holidays.list(
        workspace_id="w1", assigned_to="u1", page=1, page_size=200
    )
    assert_wired(
        capture,
        resource="holidays",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/holidays",
        query={"assigned-to": ["u1"], "page": ["1"], "page-size": ["200"]},
    )
    assert [h.id for h in holidays] == ["h1"]


async def test_list_default_workspace() -> None:
    client, capture = make_client(json=[])
    await client.holidays.list()
    assert "/workspaces/w-default/holidays" in str(capture.request.url)


async def test_list_in_period_query_wire_names() -> None:
    client, capture = make_client(json=[HOLIDAY_JSON])
    holidays = await client.holidays.list_in_period(
        workspace_id="w1",
        assigned_to="u1",
        start="2026-01-01T00:00:00Z",
        end="2026-12-31T23:59:59Z",
    )
    assert_wired(
        capture,
        resource="holidays",
        method="list_in_period",
        url="https://api.clockify.me/api/v1/workspaces/w1/holidays/in-period",
        query={
            "assigned-to": ["u1"],
            "start": ["2026-01-01T00:00:00Z"],
            "end": ["2026-12-31T23:59:59Z"],
        },
    )
    assert [h.id for h in holidays] == ["h1"]


async def test_update_sends_exact_body() -> None:
    client, capture = make_client(json=HOLIDAY_JSON)
    body = {
        "name": "New Year",
        "datePeriod": {"startDate": "2026-01-01", "endDate": "2026-01-01"},
        "occursAnnually": True,
        "users": {"contains": "CONTAINS", "ids": ["u1"], "status": "ALL"},
    }
    await client.holidays.update("h1", body, workspace_id="w1")
    assert_wired(
        capture,
        resource="holidays",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/holidays/h1",
    )
    assert capture.sent_json() == body
