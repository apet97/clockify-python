"""Public-method wiring: shared_reports (5 operations)."""

from clockify.models import SharedReport, SharedReportListEnvelope

from ._harness import assert_wired, make_client

COVERED = {
    "postWorkspacesWorkspaceIdSharedReports",
    "deleteWorkspacesWorkspaceIdSharedReportsSharedReportId",
    "getWorkspacesWorkspaceIdSharedReports",
    "putWorkspacesWorkspaceIdSharedReportsSharedReportId",
    "getSharedReportsSharedReportId",
}

REPORT_JSON = {"id": "sr1", "name": "Q1", "workspaceId": "w1"}
CREATE_BODY = {
    "name": "Q1",
    "type": "SUMMARY",
    "filter": {
        "dateRangeStart": "2026-01-01T00:00:00Z",
        "dateRangeEnd": "2026-01-07T23:59:59Z",
        "exportType": "JSON",
    },
}


async def test_create_on_reports_host() -> None:
    client, capture = make_client(json=REPORT_JSON)
    report = await client.shared_reports.create(CREATE_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="shared_reports",
        method="create",
        url="https://reports.api.clockify.me/v1/workspaces/w1/shared-reports",
    )
    sent = capture.sent_json()
    assert sent["name"] == "Q1"
    assert sent["type"] == "SUMMARY"
    assert sent["filter"]["exportType"] == "JSON"
    assert isinstance(report, SharedReport)


async def test_delete_returns_none() -> None:
    client, capture = make_client(status=204, content=b"")
    result = await client.shared_reports.delete("sr1", workspace_id="w1")
    assert_wired(
        capture,
        resource="shared_reports",
        method="delete",
        url="https://reports.api.clockify.me/v1/workspaces/w1/shared-reports/sr1",
    )
    assert result is None


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json={"reports": [REPORT_JSON], "count": 1})
    envelope = await client.shared_reports.list(
        workspace_id="w1", page=2, page_size=10, shared_reports_filter="CREATED_BY_ME"
    )
    assert_wired(
        capture,
        resource="shared_reports",
        method="list",
        url="https://reports.api.clockify.me/v1/workspaces/w1/shared-reports",
        query={
            "page": ["2"],
            "pageSize": ["10"],
            "sharedReportsFilter": ["CREATED_BY_ME"],
        },
    )
    assert isinstance(envelope, SharedReportListEnvelope)


async def test_list_default_workspace() -> None:
    client, capture = make_client(json={"reports": []})
    await client.shared_reports.list()
    assert "/workspaces/w-default/shared-reports" in str(capture.request.url)


async def test_update_merge_semantics() -> None:
    client, capture = make_client(json=REPORT_JSON)
    report = await client.shared_reports.update("sr1", CREATE_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="shared_reports",
        method="update",
        url="https://reports.api.clockify.me/v1/workspaces/w1/shared-reports/sr1",
    )
    assert capture.sent_json()["name"] == "Q1"
    assert isinstance(report, SharedReport)


async def test_view_public_json_no_workspace() -> None:
    client, capture = make_client(json={"totals": [], "groupOne": []})
    data = await client.shared_reports.view_public(
        "sr1",
        export_type="JSON",
        date_range_start="2026-01-01T00:00:00Z",
        date_range_end="2026-01-07T23:59:59Z",
        sort_column="GROUP",
        sort_order="ASCENDING",
        page=1,
        page_size=50,
    )
    assert_wired(
        capture,
        resource="shared_reports",
        method="view_public",
        url="https://reports.api.clockify.me/v1/shared-reports/sr1",
        query={
            "exportType": ["JSON"],
            "dateRangeStart": ["2026-01-01T00:00:00Z"],
            "dateRangeEnd": ["2026-01-07T23:59:59Z"],
            "sortColumn": ["GROUP"],
            "sortOrder": ["ASCENDING"],
            "page": ["1"],
            "pageSize": ["50"],
        },
    )
    assert data == {"totals": [], "groupOne": []}


async def test_view_public_csv_text() -> None:
    client, _capture = make_client(content=b"Project,Time\np1,3600\n", content_type="text/csv")
    data = await client.shared_reports.view_public("sr1", export_type="CSV")
    assert "Project,Time" in data.text
