# pyright: reportMissingParameterType=false, reportUnknownParameterType=false, reportAttributeAccessIssue=false, reportUnusedImport=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
"""End-to-end in-memory tests for the five curated workflows."""

import httpx

from mcp import Client

from .conftest import MockBackend, result_json

ME = {
    "id": "u1",
    "name": "Alex",
    "email": "alex@example.com",
    "defaultWorkspace": "w-test",
    "activeWorkspace": "w-test",
    "status": "ACTIVE",
}
WORKSPACE = {"id": "w-test", "name": "Sandbox"}


async def test_status_reports_user_workspace_and_timers(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    backend.respond_by_path(
        {
            "/user": ME,
            "/workspaces/w-test": WORKSPACE,
            "/time-entries/status/in-progress": [
                {
                    "id": "e1",
                    "userId": "u1",
                    "description": "working",
                    "timeInterval": {"start": "2026-08-12T08:00:00Z", "end": None},
                }
            ],
        }
    )
    async with Client(server) as client:
        result = await client.call_tool("clockify_status", {})
    payload = result_json(result)
    assert payload["user"]["id"] == "u1"
    assert payload["workspace"] == {"id": "w-test", "name": "Sandbox"}
    assert payload["running_entries"][0]["id"] == "e1"


async def test_workspace_overview_counts_are_bounded_and_honest(
    server, backend: MockBackend
) -> None:  # type: ignore[no-untyped-def]
    def responder(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/workspaces/w-test"):
            return httpx.Response(200, json=WORKSPACE)
        if path.endswith("/users"):
            assert request.url.params["page-size"] == "50"
            return httpx.Response(
                200,
                json=[
                    {"id": f"u{i}", "name": "U", "email": "u@example.com", "status": "ACTIVE"}
                    for i in range(50)
                ],
            )
        if path.endswith("/projects"):
            return httpx.Response(
                200,
                json=[
                    {
                        "id": "p1",
                        "name": "P",
                        "archived": False,
                        "billable": True,
                        "color": "#000000",
                        "public": True,
                        "template": False,
                        "workspaceId": "w-test",
                    }
                ],
            )
        if path.endswith("/tags"):
            return httpx.Response(200, json=[])
        return httpx.Response(200, json=[])

    backend.responder = responder
    async with Client(server) as client:
        result = await client.call_tool("clockify_workspace_overview", {})
    payload = result_json(result)
    assert payload["users"] == {"count": 50, "exact": False}  # full page -> more may exist
    assert payload["projects"] == {"count": 1, "exact": True}
    assert payload["tags"] == {"count": 0, "exact": True}


async def test_review_day_uses_wall_clock_window(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    backend.respond_by_path(
        {
            "/user/u1/time-entries": [
                {
                    "id": "e1",
                    "description": "d",
                    "billable": False,
                    "isLocked": False,
                    "type": "REGULAR",
                    "userId": "u1",
                    "workspaceId": "w-test",
                    "timeInterval": {
                        "start": "2026-08-11T22:30:00Z",
                        "end": "2026-08-11T23:00:00Z",
                        "duration": "PT30M",
                    },
                }
            ],
            "/user": ME,
        }
    )
    async with Client(server) as client:
        result = await client.call_tool(
            "clockify_review_day",
            {"day": "2026-08-12", "timezone_name": "Europe/Belgrade", "user_id": "u1"},
        )
    payload = result_json(result)
    # Belgrade is UTC+2 in August: the wall-clock day starts at 22:00Z the day before.
    assert payload["window"] == {
        "start": "2026-08-11T22:00:00Z",
        "end": "2026-08-12T22:00:00Z",
    }
    assert payload["entry_count"] == 1
    entries_request = next(
        r for r in backend.requests if "/time-entries" in r.url.path and "u1" in r.url.path
    )
    assert entries_request.url.params["start"] == "2026-08-11T22:00:00Z"
    assert entries_request.url.params["end"] == "2026-08-12T22:00:00Z"


async def test_review_day_rejects_bad_inputs_before_network(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    async with Client(server) as client:
        bad_date = await client.call_tool("clockify_review_day", {"day": "12/08/2026"})
        bad_zone = await client.call_tool(
            "clockify_review_day", {"day": "2026-08-12", "timezone_name": "Mars/Olympus"}
        )
    assert bad_date.is_error and "ISO date" in bad_date.content[0].text
    assert bad_zone.is_error and "timezone" in bad_zone.content[0].text
    assert backend.requests == []


async def test_review_week_covers_exactly_seven_days(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    def responder(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/reports/weekly"):
            import json

            body = json.loads(request.content)
            assert body["dateRangeStart"] == "2026-08-10T00:00:00Z"
            assert body["dateRangeEnd"] == "2026-08-17T00:00:00Z"  # exactly 7 days
            return httpx.Response(200, json={"totals": [], "groupOne": []})
        if "/time-entries" in request.url.path:
            return httpx.Response(200, json=[])
        return httpx.Response(200, json=ME)

    backend.responder = responder
    async with Client(server) as client:
        result = await client.call_tool(
            "clockify_review_week", {"start_day": "2026-08-10", "user_id": "u1"}
        )
    payload = result_json(result)
    assert payload["window"]["days"] == 7
    assert any(r.url.path.endswith("/reports/weekly") for r in backend.requests)


async def test_doctor_reports_failing_credential_without_leaking(
    server, backend: MockBackend
) -> None:  # type: ignore[no-untyped-def]
    backend.responder = lambda request: httpx.Response(401, json={"message": "bad key"})
    async with Client(server) as client:
        result = await client.call_tool("clockify_doctor", {})
    payload = result_json(result)
    assert payload["healthy"] is False
    checks = {c["check"]: c for c in payload["checks"]}
    assert checks["credential configured"]["ok"] is True
    assert checks["credential works"]["ok"] is False
    assert "test-key" not in str(payload)


async def test_doctor_happy_path(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    backend.respond_by_path({"/workspaces/w-test": WORKSPACE, "/user": ME})
    async with Client(server) as client:
        result = await client.call_tool("clockify_doctor", {})
    payload = result_json(result)
    assert payload["healthy"] is True


async def test_workflows_cannot_mutate(backend: MockBackend) -> None:
    """The workflow layer holds only the restricted client; a write raises."""
    import pytest

    from clockify.errors import ClockifyReadOnlyViolation

    from .conftest import make_mock_client

    client = make_mock_client(backend)
    with pytest.raises(ClockifyReadOnlyViolation):
        await client.time_entries.create({"start": "2026-08-12T08:00:00Z"})
    assert backend.requests == []
