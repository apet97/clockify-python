# pyright: reportMissingParameterType=false, reportUnknownParameterType=false, reportAttributeAccessIssue=false, reportUnusedImport=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
"""The read MCP's structural guarantees."""

import pytest

from clockify.errors import ClockifyReadOnlyViolation
from clockify.operations.model import ResponseKind
from clockify.operations.registry import ALL_OPERATIONS, BY_ID

from .conftest import MockBackend, make_mock_client

EXPECTED_RAW_TOOLS = {
    f"clockify_{op.resource}_{op.sdk_method}"
    for op in ALL_OPERATIONS
    if not op.semantics.mutates and op.response_kind is not ResponseKind.BYTES
}
WORKFLOW_TOOLS = {
    "clockify_status",
    "clockify_workspace_overview",
    "clockify_review_day",
    "clockify_review_week",
    "clockify_doctor",
}


async def test_exactly_60_raw_read_tools_plus_5_workflows(server) -> None:  # type: ignore[no-untyped-def]
    tools = {tool.name for tool in await server.list_tools()}
    assert len(EXPECTED_RAW_TOOLS) == 60
    assert tools == EXPECTED_RAW_TOOLS | WORKFLOW_TOOLS
    assert len(tools) == 65


async def test_every_raw_tool_maps_to_a_non_mutating_operation(server) -> None:  # type: ignore[no-untyped-def]
    by_tool_name = {f"clockify_{op.resource}_{op.sdk_method}": op for op in ALL_OPERATIONS}
    for tool in await server.list_tools():
        if tool.name in WORKFLOW_TOOLS:
            continue
        operation = by_tool_name[tool.name]
        assert operation.semantics.mutates is False, tool.name
        assert operation.response_kind is not ResponseKind.BYTES, tool.name


async def test_annotations_are_read_only_hints(server) -> None:  # type: ignore[no-untyped-def]
    for tool in await server.list_tools():
        annotations = tool.annotations
        assert annotations is not None, tool.name
        assert annotations.read_only_hint is True, tool.name
        assert annotations.destructive_hint is False, tool.name
        assert annotations.open_world_hint is True, tool.name


async def test_binary_reads_are_not_registered(server) -> None:  # type: ignore[no-untyped-def]
    tools = {tool.name for tool in await server.list_tools()}
    assert "clockify_expenses_download_receipt" not in tools
    assert "clockify_invoices_export" not in tools


async def test_deliberate_mutation_is_blocked_before_http(backend: MockBackend) -> None:
    """Even a miswired caller holding the restricted client cannot mutate."""
    client = make_mock_client(backend)
    with pytest.raises(ClockifyReadOnlyViolation):
        await client.tags.create({"name": "evil"}, workspace_id="w-test")
    with pytest.raises(ClockifyReadOnlyViolation):
        await client.raw.call(
            "deleteWorkspacesWorkspaceIdTagsTagId",
            path={"workspaceId": "w-test", "tagId": "t1"},
        )
    assert backend.requests == [], "no mutation may reach the transport"


async def test_get_verb_mutation_trap_blocked(backend: MockBackend) -> None:
    """The boundary consults semantics, not the verb: a GET write is refused too."""
    client = make_mock_client(backend)
    get_writes = [op for op in ALL_OPERATIONS if op.semantics.mutates and op.http_method == "GET"]
    # The real surface has no GET write today; prove the boundary via a PATCH
    # with an empty body and via semantics directly.
    assert BY_ID["patchWorkspacesWorkspaceIdWebhooksWebhookIdToken"].semantics.mutates
    with pytest.raises(ClockifyReadOnlyViolation):
        await client.webhooks.rotate_token("wh1", workspace_id="w-test")
    assert backend.requests == []
    assert get_writes == []  # documents today's surface; trap covered in transport tests


async def test_server_construction_makes_no_clockify_request(backend: MockBackend) -> None:
    from clockify_mcp.server import build_read_only_server

    from .conftest import TEST_CONFIG

    build_read_only_server(TEST_CONFIG, client=make_mock_client(backend))
    assert backend.requests == []


async def test_missing_credentials_fail_without_leaking(monkeypatch: pytest.MonkeyPatch) -> None:
    from clockify.errors import ClockifyConfigurationError
    from clockify_mcp.context import ServerConfig, build_read_only_client

    config = ServerConfig(api_key=None, addon_token=None, workspace_id=None)
    with pytest.raises(ClockifyConfigurationError) as info:
        build_read_only_client(config)
    assert "CLOCKIFY_API_KEY" in str(info.value)


async def test_no_write_module_is_imported_by_the_read_server() -> None:
    """Checked in a fresh interpreter: the test session itself imports writes tests."""
    import subprocess
    import sys

    code = (
        "import sys; import clockify_mcp.server, clockify_mcp.tools; "
        "bad = [m for m in sys.modules if m.startswith('clockify_mcp.writes')]; "
        "assert bad == [], bad"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_read_executor_compatibility_facade_preserves_identity() -> None:
    from clockify._transport.executor import ReadOnlyExecutor as TransportReadOnlyExecutor
    from clockify_mcp.read_executor import ReadOnlyExecutor as MCPReadOnlyExecutor

    assert MCPReadOnlyExecutor is TransportReadOnlyExecutor


async def test_corrected_raw_tool_schemas(server) -> None:  # type: ignore[no-untyped-def]
    tools = {tool.name: tool.input_schema for tool in await server.list_tools()}

    for name in (
        "clockify_custom_fields_list_for_workspace",
        "clockify_custom_fields_list_for_project",
    ):
        assert {"type": "array", "items": {"type": "string"}} in tools[name]["properties"][
            "entity_type"
        ]["anyOf"]
    for name in (
        "clockify_projects_list",
        "clockify_tags_list",
        "clockify_tasks_list",
    ):
        assert {"type": "boolean"} in tools[name]["properties"]["strict_name_search"]["anyOf"]
    assert {"type": "string"} in tools["clockify_tags_list"]["properties"]["excluded_ids"]["anyOf"]
    assert {"type": "string"} in tools["clockify_time_off_policies_list"]["properties"]["page"][
        "anyOf"
    ]
    assert {"type": "string"} in tools["clockify_users_list"]["properties"]["account_statuses"][
        "anyOf"
    ]
    assert tools["clockify_users_list"]["properties"]["include_roles"] == {
        "default": False,
        "title": "Include Roles",
        "type": "boolean",
    }
    assert tools["clockify_webhooks_list_event_statuses"]["properties"]["statuses"]["anyOf"][0] == {
        "enum": ["SUCCEEDED", "RETRYING", "FAILED"],
        "type": "string",
    }

    for name in (
        "clockify_entity_changes_list_created",
        "clockify_entity_changes_list_deleted",
        "clockify_entity_changes_list_updated",
    ):
        assert set(tools[name]["required"]) == {"type"}
    assert set(tools["clockify_holidays_list_in_period"]["required"]) == {
        "assigned_to",
        "start",
        "end",
    }
    assert set(tools["clockify_scheduling_get_project_totals"]["required"]) == {
        "project_id",
        "start",
        "end",
    }
    assert set(tools["clockify_scheduling_get_user_capacity"]["required"]) == {
        "user_id",
        "start",
        "end",
    }
    assert set(tools["clockify_scheduling_list_assignments"]["required"]) == {
        "start",
        "end",
    }
