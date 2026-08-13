# pyright: reportPrivateUsage=false
"""Shared write runner: multi-step order, partial failure, routine tier."""

from types import SimpleNamespace
from typing import Any

import pytest

from clockify._transport.auth import Credential
from clockify.errors import ClockifyAPIError, ClockifyTransportError
from clockify_mcp.writes.gate import WriteGate
from clockify_mcp.writes.nonce_store import WriteSafetyError
from clockify_mcp.writes.plan import WriteStep
from clockify_mcp.writes.plans import build_plan, build_step, make_revalidator
from clockify_mcp.writes.principal import new_process_secret
from clockify_mcp.writes.runner import (
    GuardedWriteSpec,
    WriteDeps,
    run_guarded_write,
    run_routine_write,
)

WORKSPACE = "6" * 24
PROJECT = "7" * 24

APPROVE = SimpleNamespace(action="accept", data=SimpleNamespace(decision="approve"))
REJECT = SimpleNamespace(action="accept", data=SimpleNamespace(decision="reject"))


def archive_then_delete_plan():  # type: ignore[no-untyped-def]
    """A real two-step lifecycle plan: archive the project, then delete it."""
    return build_plan(
        title="Delete project",
        summary=f"Archive then delete project {PROJECT}",
        steps=(
            build_step(
                "updateProject",
                path_args={"workspaceId": WORKSPACE, "projectId": PROJECT},
                body={"archived": True, "name": "Doomed"},
            ),
            build_step(
                "deleteProject",
                path_args={"workspaceId": WORKSPACE, "projectId": PROJECT},
            ),
        ),
    )


class FakeSender:
    """Scripted per-step outcomes: 'ok', an int status, or an exception."""

    def __init__(self, script: list[Any]) -> None:
        self.script = script
        self.sent: list[WriteStep] = []

    async def __call__(self, step: WriteStep) -> tuple[int, str | None, Any]:
        action = self.script[len(self.sent)]
        self.sent.append(step)
        if isinstance(action, BaseException):
            raise action
        if action == "ok":
            return 200, f"req-{len(self.sent)}", {"id": PROJECT}
        return int(action), None, {"error": action}


def make_deps(script: list[Any]) -> tuple[WriteDeps, FakeSender]:
    gate = WriteGate(
        process_secret=new_process_secret(),
        credential=Credential(api_key="runner-test-key"),
    )
    sender = FakeSender(script)
    read_client: Any = None  # runner tests never touch the read client
    return WriteDeps(read_client=read_client, gate=gate, sender=sender), sender


def spec() -> GuardedWriteSpec:
    return GuardedWriteSpec(
        tool_name="clockify_projects_delete",
        revalidate=make_revalidator(("updateProject", "deleteProject")),
    )


async def prepare(deps: WriteDeps):  # type: ignore[no-untyped-def]
    return await deps.gate.prepare(
        tool_name="clockify_projects_delete",
        arguments={"project_id": PROJECT},
        workspace_id=WORKSPACE,
        plan=archive_then_delete_plan(),
    )


async def test_multi_step_dispatches_in_order() -> None:
    deps, sender = make_deps(["ok", "ok"])
    result = await run_guarded_write(spec(), deps, prepared=await prepare(deps), approval=APPROVE)
    assert result.state == "succeeded"
    assert [step.operation_id for step in sender.sent] == ["updateProject", "deleteProject"]
    assert [applied.index for applied in result.applied_steps] == [0, 1]
    assert result.request_ids == ["req-1", "req-2"]


async def test_second_step_api_error_is_partial_failure() -> None:
    deps, sender = make_deps(
        [
            "ok",
            ClockifyAPIError("HTTP 400", status_code=400, operation_id="deleteProject"),
        ]
    )
    result = await run_guarded_write(spec(), deps, prepared=await prepare(deps), approval=APPROVE)
    assert result.state == "partial_failure"
    assert len(result.applied_steps) == 1
    assert result.failed_step is not None and result.failed_step.index == 1
    assert len(sender.sent) == 2


async def test_first_step_api_error_is_failed() -> None:
    deps, sender = make_deps(
        [ClockifyAPIError("HTTP 403", status_code=403, operation_id="updateProject")]
    )
    result = await run_guarded_write(spec(), deps, prepared=await prepare(deps), approval=APPROVE)
    assert result.state == "failed"
    assert result.applied_steps == []
    assert len(sender.sent) == 1  # the delete never dispatched


async def test_transport_ambiguity_is_outcome_unknown() -> None:
    deps, sender = make_deps(["ok", ClockifyTransportError("connection dropped")])
    result = await run_guarded_write(spec(), deps, prepared=await prepare(deps), approval=APPROVE)
    assert result.state == "outcome_unknown"
    assert len(result.applied_steps) == 1
    assert result.next_actions
    assert len(sender.sent) == 2


async def test_reject_cancels_without_dispatch() -> None:
    deps, sender = make_deps([])
    result = await run_guarded_write(spec(), deps, prepared=await prepare(deps), approval=REJECT)
    assert result.state == "rejected"
    assert sender.sent == []


async def test_replay_after_consume_fails_closed() -> None:
    deps, sender = make_deps(["ok", "ok"])
    prepared = await prepare(deps)
    first = await run_guarded_write(spec(), deps, prepared=prepared, approval=APPROVE)
    assert first.state == "succeeded"
    replay = await run_guarded_write(spec(), deps, prepared=prepared, approval=APPROVE)
    assert replay.state == "failed_before_dispatch"
    assert len(sender.sent) == 2  # no further dispatch


async def test_revalidation_failure_never_dispatches() -> None:
    deps, sender = make_deps(["ok", "ok"])
    wrong_shape = GuardedWriteSpec(
        tool_name="clockify_projects_delete",
        revalidate=make_revalidator(("deleteProject",)),  # expects one step, plan has two
    )
    result = await run_guarded_write(
        wrong_shape, deps, prepared=await prepare(deps), approval=APPROVE
    )
    assert result.state == "failed_before_dispatch"
    assert sender.sent == []


async def test_routine_write_executes_without_gate() -> None:
    deps, sender = make_deps(["ok"])
    plan = build_plan(
        title="Start timer",
        summary="Start a timer",
        steps=(
            build_step(
                "postWorkspacesWorkspaceIdTimeEntries",
                path_args={"workspaceId": WORKSPACE},
                body={"start": "2026-08-13T08:00:00Z"},
            ),
        ),
    )
    result = await run_routine_write("clockify_start_work", plan, deps)
    assert result.state == "succeeded"
    assert result.confirmation_id == ""
    assert len(sender.sent) == 1


async def test_routine_write_refuses_read_operations() -> None:
    deps, sender = make_deps(["ok"])
    read_step = WriteStep(
        operation_id="getWorkspacesWorkspaceIdTags",
        path_arguments=(("workspaceId", WORKSPACE),),
    )
    plan = build_plan(
        title="Sneaky read",
        summary="A read through the write path",
        steps=(
            build_step(
                "postWorkspacesWorkspaceIdTags",
                path_args={"workspaceId": WORKSPACE},
                body={"name": "x"},
            ),
        ),
    )
    object.__setattr__(plan, "steps", (read_step,))
    with pytest.raises(WriteSafetyError, match="read operations"):
        await run_routine_write("clockify_sneaky", plan, deps)
    assert sender.sent == []
