# pyright: reportMissingParameterType=false, reportUnknownParameterType=false, reportAttributeAccessIssue=false, reportUnusedImport=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
"""In-memory client calls through representative raw read tools."""

from mcp import Client

from .conftest import MockBackend, result_json


async def test_get_read_tool_end_to_end(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    backend.respond_json([{"id": "t1", "name": "billing", "archived": False}])
    async with Client(server) as client:
        result = await client.call_tool("clockify_tags_list", {"archived": False})
    payload = result_json(result)
    assert payload["operation_id"] == "getWorkspacesWorkspaceIdTags"
    assert payload["data"][0]["id"] == "t1"
    request = backend.requests[0]
    assert request.url.path.endswith("/workspaces/w-test/tags")
    assert request.url.params["archived"] == "false"
    assert request.headers["X-Api-Key"] == "test-key"


async def test_post_read_tool_sends_body(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    backend.respond_json({"timeentries": []})
    async with Client(server) as client:
        result = await client.call_tool(
            "clockify_reports_summary",
            {
                "body": {
                    "dateRangeStart": "2026-08-01T00:00:00Z",
                    "dateRangeEnd": "2026-08-08T00:00:00Z",
                    "summaryFilter": {"groups": ["USER"]},
                }
            },
        )
    payload = result_json(result)
    assert payload["operation_id"] == "generateSummaryReport"
    request = backend.requests[0]
    assert request.method == "POST"
    assert request.url.host == "reports.api.clockify.me"
    assert b"dateRangeStart" in request.content


async def test_last_page_header_is_surfaced(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    import httpx

    backend.responder = lambda request: httpx.Response(200, json=[], headers={"Last-Page": "true"})
    async with Client(server) as client:
        result = await client.call_tool("clockify_clients_list", {})
    assert result_json(result)["last_page"] is True


async def test_shared_report_view_rejects_binary_formats_before_network(
    server, backend: MockBackend
) -> None:  # type: ignore[no-untyped-def]
    async with Client(server, raise_exceptions=False) as client:
        result = await client.call_tool(
            "clockify_shared_reports_view_public",
            {"shared_report_id": "sr1", "format": "PDF"},
        )
    assert result.is_error
    assert "JSON or CSV" in result.content[0].text
    assert backend.requests == [], "rejected before any network call"


async def test_api_error_becomes_safe_tool_error(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    import httpx

    backend.responder = lambda request: httpx.Response(403, json={"message": "no access"})
    async with Client(server) as client:
        result = await client.call_tool("clockify_tags_list", {})
    assert result.is_error
    text = result.content[0].text
    assert "403" in text
    assert "test-key" not in text  # never leak the credential


async def test_missing_workspace_produces_setup_error(backend: MockBackend) -> None:
    from clockify_mcp.server import build_read_only_server

    from .conftest import TEST_CONFIG, make_mock_client

    server = build_read_only_server(
        TEST_CONFIG, client=make_mock_client(backend, workspace_id=None)
    )
    async with Client(server) as client:
        result = await client.call_tool("clockify_tags_list", {})
    assert result.is_error
    assert "workspace_id" in result.content[0].text
    assert backend.requests == []
