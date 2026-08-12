"""Public-method wiring: reports (5 operations)."""

from clockify.models import (
    AttendanceReportResponse,
    DetailedReportResponse,
    ExpenseDetailedReportDtoV1,
    SummaryReportResponse,
    WeeklyReportResponse,
)

from ._harness import assert_wired, make_client

COVERED = {
    "generateAttendanceReport",
    "generateDetailedReport",
    "generateDetailedReportV1",
    "generateSummaryReport",
    "generateWeeklyReport",
}

START = "2026-01-01T00:00:00Z"
END = "2026-01-07T23:59:59Z"


async def test_attendance() -> None:
    client, capture = make_client(json={})
    result = await client.reports.attendance(
        {
            "dateRangeStart": START,
            "dateRangeEnd": END,
            "attendanceFilter": {"page": 1, "pageSize": 50},
        },
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="reports",
        method="attendance",
        url="https://reports.api.clockify.me/v1/workspaces/w1/reports/attendance",
    )
    sent = capture.sent_json()
    assert sent["dateRangeStart"] == START
    assert sent["dateRangeEnd"] == END
    assert sent["attendanceFilter"] == {"page": 1, "pageSize": 50}
    assert isinstance(result, AttendanceReportResponse)


async def test_detailed() -> None:
    client, capture = make_client(json={"totals": []})
    result = await client.reports.detailed(
        {
            "dateRangeStart": START,
            "dateRangeEnd": END,
            "detailedFilter": {"page": 1, "pageSize": 50},
        },
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="reports",
        method="detailed",
        url="https://reports.api.clockify.me/v1/workspaces/w1/reports/detailed",
    )
    assert capture.sent_json()["detailedFilter"] == {"page": 1, "pageSize": 50}
    assert isinstance(result, DetailedReportResponse)


async def test_expense_details_with_body() -> None:
    client, capture = make_client(json={})
    result = await client.reports.expense_details(
        {"dateRangeStart": START, "dateRangeEnd": END},
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="reports",
        method="expense_details",
        url="https://reports.api.clockify.me/v1/workspaces/w1/reports/expenses/detailed",
    )
    sent = capture.sent_json()
    assert sent["dateRangeStart"] == START
    assert sent["dateRangeEnd"] == END
    assert isinstance(result, ExpenseDetailedReportDtoV1)


async def test_expense_details_body_optional_default_workspace() -> None:
    client, capture = make_client(json={})
    await client.reports.expense_details()
    assert "/workspaces/w-default/reports/expenses/detailed" in str(capture.request.url)


async def test_summary() -> None:
    client, capture = make_client(json={"groupOne": []})
    result = await client.reports.summary(
        {
            "dateRangeStart": START,
            "dateRangeEnd": END,
            "summaryFilter": {"groups": ["PROJECT"]},
        },
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="reports",
        method="summary",
        url="https://reports.api.clockify.me/v1/workspaces/w1/reports/summary",
    )
    assert capture.sent_json()["summaryFilter"] == {"groups": ["PROJECT"]}
    assert isinstance(result, SummaryReportResponse)


async def test_weekly() -> None:
    client, capture = make_client(json={"totalsByDay": []})
    result = await client.reports.weekly(
        {
            "dateRangeStart": START,
            "dateRangeEnd": END,
            "weeklyFilter": {"group": "PROJECT", "subgroup": "TIME"},
        },
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="reports",
        method="weekly",
        url="https://reports.api.clockify.me/v1/workspaces/w1/reports/weekly",
    )
    assert capture.sent_json()["weeklyFilter"] == {"group": "PROJECT", "subgroup": "TIME"}
    assert isinstance(result, WeeklyReportResponse)
