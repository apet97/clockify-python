# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportArgumentType=false, reportCallIssue=false, reportUnknownVariableType=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportMissingParameterType=false
"""Safety Phase D: exact permit/step enforcement against a mock sender."""

import asyncio
from typing import Any

import httpx
import pytest

from clockify_mcp.writes.canonical import canonical_json
from clockify_mcp.writes.executor import ControlledWriteExecutor, PermitViolation
from clockify_mcp.writes.nonce_store import ExecutionPermit
from clockify_mcp.writes.plan import WritePlan, WriteStep

ARCHIVE_STEP = WriteStep(
    operation_id="updateProject",
    path_arguments=(("workspaceId", "w1"), ("projectId", "p1")),
    body_json=canonical_json({"name": "P", "archived": True, "isPublic": True}),
)
DELETE_STEP = WriteStep(
    operation_id="deleteProject",
    path_arguments=(("workspaceId", "w1"), ("projectId", "p1")),
)

LIFECYCLE_PLAN = WritePlan(
    version=1,
    title="Delete project",
    summary="Archive then delete project p1",
    effect="delete",
    scope="one entity",
    sensitivity=(),
    reversibility="irreversible",
    steps=(ARCHIVE_STEP, DELETE_STEP),
)


def make_permit(plan: WritePlan = LIFECYCLE_PLAN) -> ExecutionPermit:
    return ExecutionPermit(
        permit_id="permit-1",
        principal_id="principal-a",
        tool_name="clockify_projects_delete",
        arguments_digest="argdigest",
        plan=plan,
        consumed_at=0.0,
    )


class RecordingSender:
    def __init__(self, outcomes: list[Any] | None = None) -> None:
        self.dispatched: list[WriteStep] = []
        self.outcomes = outcomes or []

    async def __call__(self, step: WriteStep) -> tuple[int, str | None, Any]:
        self.dispatched.append(step)
        if self.outcomes:
            outcome = self.outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome
        return (200, f"req-{len(self.dispatched)}", {"ok": True})


async def test_exact_ordered_plan_dispatches() -> None:
    sender = RecordingSender()
    executor = ControlledWriteExecutor(make_permit(), sender)
    await executor.dispatch(0, ARCHIVE_STEP)
    await executor.dispatch(1, DELETE_STEP)
    assert [s.operation_id for s in sender.dispatched] == ["updateProject", "deleteProject"]
    assert executor.terminal


async def test_wrong_operation_refused_before_sender() -> None:
    sender = RecordingSender()
    executor = ControlledWriteExecutor(make_permit(), sender)
    imposter = WriteStep(
        operation_id="deleteWorkspacesWorkspaceIdClientsClientId",
        path_arguments=(("workspaceId", "w1"), ("clientId", "c1")),
    )
    with pytest.raises(PermitViolation, match="not approved"):
        await executor.dispatch(0, imposter)
    assert sender.dispatched == []


async def test_changed_body_refused() -> None:
    sender = RecordingSender()
    executor = ControlledWriteExecutor(make_permit(), sender)
    tampered = WriteStep(
        operation_id="updateProject",
        path_arguments=(("workspaceId", "w1"), ("projectId", "p1")),
        body_json=canonical_json({"name": "P", "archived": False, "isPublic": True}),
    )
    with pytest.raises(PermitViolation, match="differs from the approved plan"):
        await executor.dispatch(0, tampered)
    assert sender.dispatched == []


async def test_changed_path_refused() -> None:
    sender = RecordingSender()
    executor = ControlledWriteExecutor(make_permit(), sender)
    other_project = WriteStep(
        operation_id="updateProject",
        path_arguments=(("workspaceId", "w1"), ("projectId", "p2")),
        body_json=ARCHIVE_STEP.body_json,
    )
    with pytest.raises(PermitViolation):
        await executor.dispatch(0, other_project)
    assert sender.dispatched == []


async def test_skip_step_refused() -> None:
    sender = RecordingSender()
    executor = ControlledWriteExecutor(make_permit(), sender)
    with pytest.raises(PermitViolation, match="not the next allowed step"):
        await executor.dispatch(1, DELETE_STEP)
    assert sender.dispatched == []


async def test_repeat_step_refused() -> None:
    sender = RecordingSender()
    executor = ControlledWriteExecutor(make_permit(), sender)
    await executor.dispatch(0, ARCHIVE_STEP)
    with pytest.raises(PermitViolation):
        await executor.dispatch(0, ARCHIVE_STEP)
    assert len(sender.dispatched) == 1


async def test_extra_step_after_completion_refused() -> None:
    sender = RecordingSender()
    executor = ControlledWriteExecutor(make_permit(), sender)
    await executor.dispatch(0, ARCHIVE_STEP)
    await executor.dispatch(1, DELETE_STEP)
    with pytest.raises(PermitViolation, match="terminal"):
        await executor.dispatch(2, ARCHIVE_STEP)
    assert len(sender.dispatched) == 2


async def test_read_operation_refused_through_write_permit() -> None:
    read_step = WriteStep(
        operation_id="getProjectById",
        path_arguments=(("workspaceId", "w1"), ("projectId", "p1")),
    )
    plan = WritePlan(
        version=1,
        title="bogus",
        summary="bogus",
        effect="delete",
        scope="one entity",
        sensitivity=(),
        reversibility="unknown",
        steps=(read_step,),
    )
    sender = RecordingSender()
    executor = ControlledWriteExecutor(make_permit(plan), sender)
    with pytest.raises(PermitViolation, match="read operations may not use a write permit"):
        await executor.dispatch(0, read_step)
    assert sender.dispatched == []


async def test_http_error_is_terminal_and_not_retried() -> None:
    sender = RecordingSender(outcomes=[(500, "req-1", {"message": "boom"})])
    executor = ControlledWriteExecutor(make_permit(), sender)
    outcome = await executor.dispatch(0, ARCHIVE_STEP)
    assert outcome.status_code == 500
    assert executor.terminal
    with pytest.raises(PermitViolation):
        await executor.dispatch(1, DELETE_STEP)
    assert len(sender.dispatched) == 1  # exactly one dispatch, no retry


async def test_transport_ambiguity_is_terminal() -> None:
    sender = RecordingSender(outcomes=[httpx.ReadTimeout("mid-flight")])
    executor = ControlledWriteExecutor(make_permit(), sender)
    with pytest.raises(httpx.ReadTimeout):
        await executor.dispatch(0, ARCHIVE_STEP)
    assert executor.terminal
    with pytest.raises(PermitViolation):
        await executor.dispatch(1, DELETE_STEP)


async def test_cancellation_is_terminal_without_further_steps() -> None:
    started = asyncio.Event()

    async def hanging_sender(step: WriteStep) -> tuple[int, str | None, Any]:
        started.set()
        await asyncio.sleep(30)
        return (200, None, None)

    executor = ControlledWriteExecutor(make_permit(), hanging_sender)
    task = asyncio.create_task(executor.dispatch(0, ARCHIVE_STEP))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert executor.terminal


async def test_partial_failure_shape() -> None:
    """Step 1 applies, step 2 fails: exactly one dispatch each, no rollback dispatch."""
    sender = RecordingSender(
        outcomes=[(200, "r1", {"archived": True}), (409, "r2", {"message": "conflict"})]
    )
    executor = ControlledWriteExecutor(make_permit(), sender)
    first = await executor.dispatch(0, ARCHIVE_STEP)
    second = await executor.dispatch(1, DELETE_STEP)
    assert first.status_code == 200
    assert second.status_code == 409
    assert executor.terminal
    assert len(sender.dispatched) == 2  # and nothing more — no rollback mutation
