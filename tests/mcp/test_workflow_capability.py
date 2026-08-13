# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false
"""Review finding F3: workflows hold a restricted read capability.

Four proofs: (1) tool registration hands workflows a `WorkflowReadClient`,
never a `ClockifyClient`; (2) that capability's ordinary API exposes no raw
dispatch, no executor, and no mutating methods; (3) a mutation that does reach
`ReadOnlyExecutor` is rejected before the transport; (4) an invariant tripwire
runs every workflow end-to-end and asserts no mutating request was dispatched
(this is the test that catches a workflow edited to bypass the capability).
"""

import httpx
import pytest

from clockify.client import ClockifyClient
from clockify.errors import ClockifyReadOnlyViolation
from clockify.operations.tags import TAGS_CREATE
from clockify_mcp.read_capability import WorkflowReadClient
from mcp import Client

from .conftest import MockBackend, make_mock_client

ME = {
    "id": "u1",
    "name": "Alex",
    "email": "alex@example.com",
    "defaultWorkspace": "w-test",
    "activeWorkspace": "w-test",
    "status": "ACTIVE",
}


async def test_workflows_receive_the_restricted_capability(
    backend: MockBackend, monkeypatch: pytest.MonkeyPatch
) -> None:
    import clockify_mcp.tools.workflows as workflows_module
    from clockify_mcp.workflows.status import status as real_status

    seen: list[object] = []

    async def spying_status(client):  # type: ignore[no-untyped-def]
        seen.append(client)
        return await real_status(client)

    monkeypatch.setattr(workflows_module, "status", spying_status)
    from mcp.server import MCPServer

    server = MCPServer(name="capability-test")
    mock_client = make_mock_client(backend)
    workflows_module.register_workflows(
        server,
        mock_client,
        __import__("clockify_mcp.context", fromlist=["x"]).ServerConfig(
            api_key="test-key", addon_token=None, workspace_id="w-test"
        ),
    )
    backend.respond_by_path(
        {"/user": ME, "/workspaces/w-test": {"id": "w-test", "name": "S"}, "/time-entries": []}
    )
    async with Client(server) as client:
        await client.call_tool("clockify_status", {})
    assert len(seen) == 1
    assert isinstance(seen[0], WorkflowReadClient)
    assert not isinstance(seen[0], ClockifyClient)


def test_capability_surface_is_reads_only(backend: MockBackend) -> None:
    capability = WorkflowReadClient(make_mock_client(backend))
    # No raw dispatch, no executor, no client handle on the ordinary API.
    for forbidden in ("raw", "_executor", "_client", "call"):
        assert not hasattr(capability, forbidden), forbidden
    # Slotted: nothing beyond the declared read namespaces exists or can be added.
    assert not hasattr(capability, "__dict__")
    expected = {
        "workspace_id",
        "users",
        "workspaces",
        "time_entries",
        "projects",
        "tags",
        "reports",
        "clients",
        "tasks",
        "expense_categories",
        "time_off_policies",
    }
    assert set(WorkflowReadClient.__slots__) == expected
    # Each namespace exposes exactly its reads — no create/update/delete anywhere.
    for namespace in sorted(expected - {"workspace_id"}):
        slots = set(getattr(capability, namespace).__slots__)
        assert not slots & {"create", "update", "delete", "duplicate"}, namespace
    assert set(capability.time_entries.__slots__) == {"get", "list_in_progress", "list_for_user"}
    assert set(capability.tags.__slots__) == {"list"}


async def test_mutation_reaching_read_only_executor_is_rejected_before_transport(
    backend: MockBackend,
) -> None:
    client = make_mock_client(backend)
    with pytest.raises(ClockifyReadOnlyViolation):
        await client._executor.execute(  # pyright: ignore[reportPrivateUsage]
            TAGS_CREATE, path_args={"workspaceId": "w-test"}, body={"name": "x"}
        )
    assert backend.requests == []  # rejected before any HTTP dispatch


async def test_no_workflow_dispatches_a_mutating_request(server, backend: MockBackend) -> None:  # type: ignore[no-untyped-def]
    """Tripwire for mutant 7: run all five workflows; every request must be a read."""

    def responder(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/user"):
            return httpx.Response(200, json=ME)
        if path.endswith("/workspaces/w-test"):
            return httpx.Response(200, json={"id": "w-test", "name": "S"})
        if path.endswith("/reports/weekly"):
            return httpx.Response(200, json={"totals": [], "groupOne": []})
        return httpx.Response(200, json=[])

    backend.responder = responder
    async with Client(server) as client:
        for tool, arguments in (
            ("clockify_status", {}),
            ("clockify_workspace_overview", {}),
            ("clockify_review_day", {"day": "2026-08-12", "user_id": "u1"}),
            ("clockify_review_week", {"start_day": "2026-08-10", "user_id": "u1"}),
            ("clockify_doctor", {}),
        ):
            result = await client.call_tool(tool, arguments)
            assert not result.is_error, tool
    assert backend.requests, "workflows made no request at all"
    for request in backend.requests:
        is_get = request.method == "GET"
        is_post_read = request.method == "POST" and "/reports/" in request.url.path
        assert is_get or is_post_read, f"mutating dispatch: {request.method} {request.url.path}"
