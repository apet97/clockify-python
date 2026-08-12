# pyright: reportUnusedFunction=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false, reportCallIssue=false, reportArgumentType=false, reportGeneralTypeIssues=false, reportOptionalIterable=false
"""Safety Phase C: resolver/protocol integration with a fake no-op write.

The fake tool exercises the full production gate (prepare -> Elicit approval ->
atomic consume -> controlled executor) against an in-memory mutation counter,
never real HTTP.
"""

from typing import Annotated, Any, Literal

import pytest
from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve
from mcp.server.request_state import RequestStateSecurity
from mcp.types import ElicitResult
from pydantic import BaseModel

from clockify._transport.auth import Credential
from clockify_mcp.writes.canonical import canonical_json
from clockify_mcp.writes.executor import ControlledWriteExecutor
from clockify_mcp.writes.gate import WriteGate, is_approved
from clockify_mcp.writes.plan import (
    Precondition,
    PreparedWrite,
    WritePlan,
    WriteStep,
    render_preview,
)
from clockify_mcp.writes.principal import AUDIENCE, new_process_secret
from mcp import Client


class WriteApproval(BaseModel):
    decision: Literal["approve", "reject"]


class FakeClockify:
    """In-memory 'API': counts mutations; supplies drifting current state."""

    def __init__(self) -> None:
        self.mutations: list[WriteStep] = []
        self.current_state = {"name": "old", "archived": False}

    async def send(self, step: WriteStep) -> tuple[int, str | None, Any]:
        self.mutations.append(step)
        return (201, "req-1", {"id": "t-new"})


def build_write_server(fake: FakeClockify) -> tuple[MCPServer, WriteGate]:
    process_secret = new_process_secret()
    credential = Credential(api_key="sacrificial-key")
    gate = WriteGate(process_secret=process_secret, credential=credential)
    security = RequestStateSecurity(
        keys=[process_secret],
        ttl=300.0,
        bind_principal=lambda _ctx: gate.principal_id,
        audience=AUDIENCE,
    )
    server = MCPServer(name="write-spike", request_state_security=security)

    def build_plan(name: str) -> WritePlan:
        # Precondition fingerprint makes the plan digest drift with state.
        return WritePlan(
            version=1,
            title="Create tag",
            summary=f"Create tag {name!r}",
            effect="create",
            scope="one entity",
            sensitivity=(),
            reversibility="reversible",
            steps=(
                WriteStep(
                    operation_id="postWorkspacesWorkspaceIdTags",
                    path_arguments=(("workspaceId", "w1"),),
                    body_json=canonical_json({"name": name}),
                ),
            ),
            preconditions=(
                Precondition(
                    "workspace state",
                    fingerprint=canonical_json(fake.current_state).hex(),
                ),
            ),
        )

    async def prepare_write(name: str) -> PreparedWrite:
        return await gate.prepare(
            tool_name="fake_tags_create",
            arguments={"name": name},
            workspace_id="w1",
            plan=build_plan(name),
        )

    def ask_for_approval(
        prepared: Annotated[PreparedWrite, Resolve(prepare_write)],
    ) -> Elicit[WriteApproval]:
        return Elicit(message=render_preview(prepared), schema=WriteApproval)

    @server.tool(name="fake_tags_create")
    async def fake_tags_create(
        name: str,
        prepared: Annotated[PreparedWrite, Resolve(prepare_write)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_for_approval)],
    ) -> dict[str, Any]:
        if not is_approved(approval):
            await gate.cancel(prepared)
            return {"state": "rejected", "confirmation_id": prepared.nonce[:12]}
        permit = await gate.consume(prepared)
        executor = ControlledWriteExecutor(permit, fake.send)
        outcome = await executor.dispatch(0, permit.plan.steps[0])
        return {
            "state": "succeeded",
            "status_code": outcome.status_code,
            "confirmation_id": prepared.nonce[:12],
        }

    return server, gate


def approve_callback(previews: list[str] | None = None):  # type: ignore[no-untyped-def]
    async def callback(context, params):  # type: ignore[no-untyped-def]
        if previews is not None:
            previews.append(params.message)
        return ElicitResult(action="accept", content={"decision": "approve"})

    return callback


async def test_modern_flow_one_approval_one_mutation() -> None:
    fake = FakeClockify()
    server, _ = build_write_server(fake)
    previews: list[str] = []
    async with Client(server, elicitation_callback=approve_callback(previews)) as client:
        result = await client.call_tool("fake_tags_create", {"name": "billing"})
    assert not result.is_error
    assert len(fake.mutations) == 1
    assert "Action: Create tag" in previews[0]
    assert "Confirmation ID:" in previews[0]


async def test_legacy_flow_same_resolver() -> None:
    fake = FakeClockify()
    server, _ = build_write_server(fake)
    async with Client(server, elicitation_callback=approve_callback(), mode="legacy") as client:
        result = await client.call_tool("fake_tags_create", {"name": "legacy-tag"})
    assert not result.is_error
    assert len(fake.mutations) == 1


async def test_approval_is_model_invisible() -> None:
    fake = FakeClockify()
    server, _ = build_write_server(fake)
    (tool,) = await server.list_tools()
    properties = tool.input_schema.get("properties", {})
    assert set(properties) == {"name"}  # prepared/approval resolved, never arguments


async def test_rejected_decision_performs_no_mutation() -> None:
    fake = FakeClockify()
    server, _ = build_write_server(fake)

    async def reject(context, params):  # type: ignore[no-untyped-def]
        return ElicitResult(action="accept", content={"decision": "reject"})

    async with Client(server, elicitation_callback=reject) as client:
        result = await client.call_tool("fake_tags_create", {"name": "x"})
    assert not result.is_error
    assert fake.mutations == []


async def test_client_decline_performs_no_mutation() -> None:
    fake = FakeClockify()
    server, _ = build_write_server(fake)

    async def decline(context, params):  # type: ignore[no-untyped-def]
        return ElicitResult(action="decline")

    async with Client(server, elicitation_callback=decline) as client:
        result = await client.call_tool("fake_tags_create", {"name": "x"})
    assert fake.mutations == []
    assert not result.is_error


async def test_client_cancel_performs_no_mutation() -> None:
    fake = FakeClockify()
    server, _ = build_write_server(fake)

    async def cancel(context, params):  # type: ignore[no-untyped-def]
        return ElicitResult(action="cancel")

    async with Client(server, elicitation_callback=cancel) as client:
        result = await client.call_tool("fake_tags_create", {"name": "x"})
    assert fake.mutations == []
    assert not result.is_error


async def test_unsupported_elicitation_fails_closed() -> None:
    fake = FakeClockify()
    server, _ = build_write_server(fake)
    failed_closed = False
    try:
        async with Client(server) as client:  # no elicitation capability declared
            result = await client.call_tool("fake_tags_create", {"name": "x"})
            failed_closed = result.is_error
    except BaseException:  # missing-capability MCPError (possibly grouped) fails closed
        failed_closed = True
    assert failed_closed
    assert fake.mutations == []


async def test_replay_of_request_state_cannot_double_mutate() -> None:
    """Byte-identical request_state replay passes integrity but hits the tombstone."""
    from mcp_types import InputRequiredResult

    fake = FakeClockify()
    server, _ = build_write_server(fake)
    async with Client(server, elicitation_callback=approve_callback()) as client:
        first = await client.session.call_tool(
            "fake_tags_create", {"name": "dup"}, allow_input_required=True
        )
        assert isinstance(first, InputRequiredResult)
        (request_id,) = first.input_requests
        responses = {request_id: {"action": "accept", "content": {"decision": "approve"}}}
        genuine = await client.session.call_tool(
            "fake_tags_create",
            {"name": "dup"},
            input_responses=responses,
            request_state=first.request_state,
            allow_input_required=True,
        )
        replay = await client.session.call_tool(
            "fake_tags_create",
            {"name": "dup"},
            input_responses=responses,
            request_state=first.request_state,
            allow_input_required=True,
        )
    assert len(fake.mutations) == 1  # exactly one dispatch ever
    assert not genuine.is_error
    # The replay either errors or asks again; it must not have mutated.
    if not isinstance(replay, InputRequiredResult):
        assert replay.is_error or "rejected" in str(replay.content)


async def test_state_drift_between_rounds_asks_again() -> None:
    """A changed plan digest invalidates the pending nonce and re-prompts."""
    from mcp_types import InputRequiredResult

    fake = FakeClockify()
    server, _ = build_write_server(fake)
    async with Client(server, elicitation_callback=approve_callback()) as client:
        first = await client.session.call_tool(
            "fake_tags_create", {"name": "drift"}, allow_input_required=True
        )
        assert isinstance(first, InputRequiredResult)
        (request_id,) = first.input_requests
        fake.current_state = {"name": "CHANGED", "archived": True}  # drift!
        responses = {request_id: {"action": "accept", "content": {"decision": "approve"}}}
        retry = await client.session.call_tool(
            "fake_tags_create",
            {"name": "drift"},
            input_responses=responses,
            request_state=first.request_state,
            allow_input_required=True,
        )
    # The changed plan produced a new question instead of executing the old one.
    assert isinstance(retry, InputRequiredResult)
    assert fake.mutations == []


async def test_identical_concurrent_calls_share_nonce_but_single_use() -> None:
    fake = FakeClockify()
    _server, gate = build_write_server(fake)
    plan_args = {
        "tool_name": "fake_tags_create",
        "arguments": {"name": "same"},
        "workspace_id": "w1",
    }
    # Direct gate-level proof of coalescing (W-16).
    from clockify_mcp.writes.canonical import canonical_json as cj

    def build() -> WritePlan:
        return WritePlan(
            version=1,
            title="t",
            summary="s",
            effect="create",
            scope="one entity",
            sensitivity=(),
            reversibility="reversible",
            steps=(
                WriteStep(
                    operation_id="postWorkspacesWorkspaceIdTags",
                    path_arguments=(("workspaceId", "w1"),),
                    body_json=cj({"name": "same"}),
                ),
            ),
        )

    first = await gate.prepare(plan=build(), **plan_args)
    second = await gate.prepare(plan=build(), **plan_args)
    assert first.nonce == second.nonce
    await gate.consume(first)
    with pytest.raises(Exception, match="confirmation_already_used"):
        await gate.consume(second)


async def test_wrong_principal_cannot_consume() -> None:
    fake = FakeClockify()
    _, gate = build_write_server(fake)
    other_gate = WriteGate(
        process_secret=new_process_secret(),
        credential=Credential(api_key="other-key"),
        store=gate.store,  # same store, different principal
    )
    plan = WritePlan(
        version=1,
        title="t",
        summary="s",
        effect="create",
        scope="one entity",
        sensitivity=(),
        reversibility="reversible",
        steps=(
            WriteStep(
                operation_id="postWorkspacesWorkspaceIdTags",
                path_arguments=(("workspaceId", "w1"),),
                body_json=canonical_json({"name": "x"}),
            ),
        ),
    )
    prepared = await gate.prepare(
        tool_name="fake_tags_create", arguments={"name": "x"}, workspace_id="w1", plan=plan
    )
    stolen = PreparedWrite(
        key=prepared.key,
        nonce=prepared.nonce,
        principal_id=other_gate.principal_id,  # attacker's identity
        tool_name=prepared.tool_name,
        workspace_id=prepared.workspace_id,
        arguments_digest=prepared.arguments_digest,
        plan=prepared.plan,
        plan_digest=prepared.plan_digest,
        issued_at=prepared.issued_at,
        expires_at=prepared.expires_at,
    )
    with pytest.raises(Exception, match="does not match"):
        await other_gate.consume(stolen)
