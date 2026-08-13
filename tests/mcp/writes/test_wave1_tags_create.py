# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportCallIssue=false, reportArgumentType=false, reportGeneralTypeIssues=false, reportOptionalIterable=false
"""Wave-1 write adapter (clockify_tags_create) through the full production gate."""

import json as jsonlib
from dataclasses import replace
from typing import Any

import httpx
from mcp.types import ElicitResult

from clockify_mcp.context import ServerConfig
from clockify_mcp.full_server import build_full_server
from clockify_mcp.writes.gate import WriteGate
from mcp import Client

from ..conftest import MockBackend, make_mock_client, result_json

CONFIG = ServerConfig(api_key="test-key", addon_token=None, workspace_id="w-test")
TAG_JSON = {"id": "t-new", "name": "wave1", "workspaceId": "w-test", "archived": False}


class WriteBackend(MockBackend):
    """Read + write mock Clockify; counts mutations separately."""

    def __init__(self) -> None:
        super().__init__()
        self.mutations: list[httpx.Request] = []

        def responder(request: httpx.Request) -> httpx.Response:
            if request.method == "POST" and request.url.path.endswith("/tags"):
                self.mutations.append(request)
                return httpx.Response(201, json=TAG_JSON)
            if request.url.path.endswith("/tags/t-new"):
                return httpx.Response(200, json=TAG_JSON)
            if request.url.path.endswith("/tags"):
                return httpx.Response(200, json=[])  # name-collision check
            return httpx.Response(200, json=[])

        self.responder = responder


def make_server(backend: WriteBackend):  # type: ignore[no-untyped-def]
    return build_full_server(
        CONFIG,
        read_client=make_mock_client(backend),
        write_http_client=httpx.AsyncClient(transport=httpx.MockTransport(backend.handler)),
    )


def approve(previews: list[str] | None = None):  # type: ignore[no-untyped-def]
    async def callback(context: Any, params: Any) -> ElicitResult:
        if previews is not None:
            previews.append(params.message)
        return ElicitResult(action="accept", content={"decision": "approve"})

    return callback


async def test_approved_create_dispatches_once_and_reconciles() -> None:
    backend = WriteBackend()
    server = make_server(backend)
    previews: list[str] = []
    async with Client(server, elicitation_callback=approve(previews)) as client:
        result = await client.call_tool("clockify_tags_create", {"name": "wave1"})
    payload = result_json(result)
    assert payload["state"] == "reconciled"
    assert payload["applied_steps"][0]["status_code"] == 201
    assert payload["data"]["id"] == "t-new"
    assert len(backend.mutations) == 1
    sent = jsonlib.loads(backend.mutations[0].content)
    assert sent == {"name": "wave1"}
    precondition_reads = [
        request
        for request in backend.requests
        if request.method == "GET" and request.url.path.endswith("/tags")
    ]
    # The modern resolver can rebuild the preview. The last read is the consumed
    # nonce's final precondition check and must still precede the POST.
    assert len(precondition_reads) >= 2
    assert all(request.url.params["strict-name-search"] == "true" for request in precondition_reads)
    assert all(request.url.params["page-size"] == "1" for request in precondition_reads)
    assert backend.requests.index(precondition_reads[-1]) < backend.requests.index(
        backend.mutations[0]
    )
    # The human saw the exact bound body before approving.
    assert '"name":"wave1"' in previews[0]
    assert "POST /workspaces/{workspaceId}/tags" in previews[0]


async def test_rejected_create_never_dispatches() -> None:
    backend = WriteBackend()
    server = make_server(backend)

    async def reject(context: Any, params: Any) -> ElicitResult:
        return ElicitResult(action="accept", content={"decision": "reject"})

    async with Client(server, elicitation_callback=reject) as client:
        result = await client.call_tool("clockify_tags_create", {"name": "nope"})
    assert result_json(result)["state"] == "rejected"
    assert backend.mutations == []


async def test_existing_name_fails_before_preview() -> None:
    backend = WriteBackend()
    original = backend.responder

    def with_existing(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path.endswith("/tags"):
            return httpx.Response(200, json=[{"id": "t-old", "name": "taken", "archived": False}])
        return original(request)

    backend.responder = with_existing
    server = make_server(backend)
    asked = {"n": 0}

    async def counting(context: Any, params: Any) -> ElicitResult:
        asked["n"] += 1
        return ElicitResult(action="accept", content={"decision": "approve"})

    async with Client(server, elicitation_callback=counting) as client:
        result = await client.call_tool("clockify_tags_create", {"name": "taken"})
    assert result.is_error
    assert "already exists" in result.content[0].text
    assert asked["n"] == 0  # failed before any approval question
    assert backend.mutations == []


async def test_state_change_after_approval_consumes_nonce_without_dispatch() -> None:
    backend = WriteBackend()
    original = backend.responder
    state_changed = False

    def changing(request: httpx.Request) -> httpx.Response:
        if state_changed and request.method == "GET" and request.url.path.endswith("/tags"):
            return httpx.Response(
                200,
                json=[{"id": "t-race", "name": "race", "archived": False}],
            )
        return original(request)

    backend.responder = changing
    server = make_server(backend)

    async def approve_after_change(context: Any, params: Any) -> ElicitResult:
        nonlocal state_changed
        state_changed = True
        return ElicitResult(action="accept", content={"decision": "approve"})

    async with Client(server, elicitation_callback=approve_after_change, mode="legacy") as client:
        result = await client.call_tool("clockify_tags_create", {"name": "race"})

    payload = result_json(result)
    assert payload["state"] == "failed_before_dispatch"
    assert payload["applied_steps"] == []
    assert payload["failed_step"] is None
    assert payload["next_actions"]
    assert "state changed" in payload["warnings"][0]
    assert backend.mutations == []


async def test_final_precondition_read_failure_never_dispatches() -> None:
    backend = WriteBackend()
    original = backend.responder
    precondition_reads = 0

    def failing_second_read(request: httpx.Request) -> httpx.Response:
        nonlocal precondition_reads
        if request.method == "GET" and request.url.path.endswith("/tags"):
            precondition_reads += 1
            if precondition_reads == 2:
                return httpx.Response(503, json={"message": "temporary"})
        return original(request)

    backend.responder = failing_second_read
    server = make_server(backend)
    async with Client(server, elicitation_callback=approve(), mode="legacy") as client:
        result = await client.call_tool("clockify_tags_create", {"name": "verify"})

    payload = result_json(result)
    assert payload["state"] == "failed_before_dispatch"
    assert payload["applied_steps"] == []
    assert payload["failed_step"] is None
    assert payload["next_actions"]
    assert "no write was sent" in payload["warnings"][0]
    assert precondition_reads == 2
    assert backend.mutations == []


async def test_malformed_consumed_plan_never_dispatches(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    backend = WriteBackend()
    original_consume = WriteGate.consume

    async def consume_with_malformed_plan(self, prepared):  # type: ignore[no-untyped-def]
        permit = await original_consume(self, prepared)
        malformed_step = replace(permit.plan.steps[0], body_json=b'{"wrong":"shape"}')
        return replace(permit, plan=replace(permit.plan, steps=(malformed_step,)))

    monkeypatch.setattr(WriteGate, "consume", consume_with_malformed_plan)
    server = make_server(backend)
    async with Client(server, elicitation_callback=approve(), mode="legacy") as client:
        result = await client.call_tool("clockify_tags_create", {"name": "shape"})

    payload = result_json(result)
    assert payload["state"] == "failed_before_dispatch"
    assert payload["applied_steps"] == []
    assert payload["failed_step"] is None
    assert "failed revalidation; no write was sent" in payload["warnings"][0]
    assert backend.mutations == []


async def test_clockify_api_error_reports_failed_state() -> None:
    backend = WriteBackend()
    original = backend.responder

    def failing(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path.endswith("/tags"):
            backend.mutations.append(request)
            return httpx.Response(400, json={"message": "bad", "code": 400})
        return original(request)

    backend.responder = failing
    server = make_server(backend)
    async with Client(server, elicitation_callback=approve()) as client:
        result = await client.call_tool("clockify_tags_create", {"name": "willfail"})
    payload = result_json(result)
    assert payload["state"] == "failed"
    assert payload["failed_step"]["status_code"] == 400
    assert len(backend.mutations) == 1  # exactly one attempt, no retry


async def test_transport_ambiguity_reports_outcome_unknown() -> None:
    backend = WriteBackend()
    original = backend.responder

    def timing_out(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path.endswith("/tags"):
            backend.mutations.append(request)
            raise httpx.ReadTimeout("mid-flight")
        return original(request)

    backend.responder = timing_out
    server = make_server(backend)
    async with Client(server, elicitation_callback=approve()) as client:
        result = await client.call_tool("clockify_tags_create", {"name": "maybe"})
    payload = result_json(result)
    assert payload["state"] == "outcome_unknown"
    assert payload["next_actions"], "must tell the caller how to read back"
    assert len(backend.mutations) == 1  # never replayed


async def test_write_tool_absent_from_read_only_server() -> None:
    from clockify_mcp.server import build_read_only_server

    backend = WriteBackend()
    read_server = build_read_only_server(CONFIG, client=make_mock_client(backend))
    tools = {tool.name for tool in await read_server.list_tools()}
    assert "clockify_tags_create" not in tools


async def test_approved_server_advertises_exactly_one_write() -> None:
    backend = WriteBackend()
    server = make_server(backend)
    tools = await server.list_tools()
    writes = [t for t in tools if t.annotations and t.annotations.read_only_hint is False]
    assert [t.name for t in writes] == ["clockify_tags_create"]
    assert len(tools) == 66  # 60 raw reads + 5 workflows + 1 write


async def test_replay_cannot_double_create() -> None:
    from mcp_types import InputRequiredResult

    backend = WriteBackend()
    server = make_server(backend)
    async with Client(server, elicitation_callback=approve()) as client:
        first = await client.session.call_tool(
            "clockify_tags_create", {"name": "once"}, allow_input_required=True
        )
        assert isinstance(first, InputRequiredResult)
        (request_id,) = first.input_requests
        responses = {request_id: {"action": "accept", "content": {"decision": "approve"}}}
        genuine = await client.session.call_tool(
            "clockify_tags_create",
            {"name": "once"},
            input_responses=responses,
            request_state=first.request_state,
            allow_input_required=True,
        )
        replay = await client.session.call_tool(
            "clockify_tags_create",
            {"name": "once"},
            input_responses=responses,
            request_state=first.request_state,
            allow_input_required=True,
        )
    assert len(backend.mutations) == 1
    assert not genuine.is_error
    if not isinstance(replay, InputRequiredResult):
        replay_payload = result_json(replay)
        assert replay_payload.get("state") in ("failed_before_dispatch", "rejected", None) or (
            replay.is_error
        )
