"""Shared execution pipeline for every write tool.

One implementation of the guarded lifecycle — reject→cancel, atomic consume,
consumed-plan revalidation, precondition recheck, ordered dispatch of every
approved step, reconciliation — so a write tool contributes only its plan
builder, its shape revalidator, and optional recheck/reconcile readers.
Routine-tier writes reuse the same dispatch-and-report tail without the gate.

Nothing here retries a mutation. A failure between steps is terminal:
``partial_failure`` reports exactly which steps applied.
"""

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Literal

from mcp.server.mcpserver import Elicit
from pydantic import BaseModel

from clockify._transport.executor import HttpExecutor
from clockify.client import ClockifyClient
from clockify.errors import ClockifyAPIError, ClockifyError
from clockify.operations.registry import BY_ID
from clockify_mcp.writes.executor import ControlledWriteExecutor, StepOutcome, StepSender
from clockify_mcp.writes.gate import WriteGate, is_approved
from clockify_mcp.writes.nonce_store import WriteSafetyError
from clockify_mcp.writes.plan import (
    Precondition,
    PreparedWrite,
    WritePlan,
    WriteStep,
    render_preview,
)
from clockify_mcp.writes.state import AppliedStep, FailedStep, WriteResult, WriteState


class WriteApproval(BaseModel):
    decision: Literal["approve", "reject"]


def elicit_approval(prepared: PreparedWrite) -> "Elicit[WriteApproval]":
    """The one approval prompt every guarded tool renders."""
    return Elicit(message=render_preview(prepared), schema=WriteApproval)


RevalidateFn = Callable[[WritePlan], None]  # raises ValueError on any mismatch
RecheckFn = Callable[[WritePlan], Awaitable[tuple[Precondition, ...]]]
ReconcileFn = Callable[[WritePlan, list[StepOutcome]], Awaitable[tuple[bool, Any]]]


@dataclass(frozen=True, slots=True)
class GuardedWriteSpec:
    """What one guarded tool must supply beyond its plan builder."""

    tool_name: str
    revalidate: RevalidateFn
    recheck: RecheckFn | None = None
    reconcile: ReconcileFn | None = None


@dataclass(frozen=True, slots=True)
class WriteDeps:
    """Shared wiring every write module receives at registration."""

    read_client: ClockifyClient
    gate: WriteGate
    sender: StepSender


def make_step_sender(write_executor: HttpExecutor) -> StepSender:
    """Adapt a WriteStep to one real dispatch through the normal transport."""

    async def send(step: WriteStep) -> tuple[int, str | None, Any]:
        operation = BY_ID[step.operation_id]
        body = json.loads(step.body_json) if step.body_json is not None else None
        query: dict[str, Any] = {}
        for key, value in step.query:  # repeated pairs become lists (explode)
            if key in query:
                existing = query[key]
                query[key] = [*existing, value] if isinstance(existing, list) else [existing, value]
            else:
                query[key] = value
        response = await write_executor.execute(
            operation,
            path_args=dict(step.path_arguments),
            query=query or None,
            body=body,
        )
        return response.status_code, response.request_id, response.data

    return send


async def _dispatch_steps(
    tool_name: str,
    confirmation: str,
    operation_ids: list[str],
    steps: tuple[WriteStep, ...],
    dispatch: Callable[[int, WriteStep], Awaitable[StepOutcome]],
) -> tuple[list[AppliedStep], list[StepOutcome], WriteResult | None]:
    """Run every step in order. Returns (applied, outcomes, terminal_failure)."""
    applied: list[AppliedStep] = []
    outcomes: list[StepOutcome] = []
    for index, step in enumerate(steps):
        try:
            outcome = await dispatch(index, step)
        except ClockifyAPIError as exc:
            failure = FailedStep(
                index=index,
                operation_id=step.operation_id,
                error=str(exc),
                status_code=exc.status_code,
            )
            state = "partial_failure" if applied else "failed"
            return (
                applied,
                outcomes,
                WriteResult(
                    state=state,
                    tool_name=tool_name,
                    confirmation_id=confirmation,
                    operation_ids=operation_ids,
                    applied_steps=applied,
                    failed_step=failure,
                ),
            )
        except (ClockifyError, WriteSafetyError) as exc:
            return (
                applied,
                outcomes,
                WriteResult(
                    state="outcome_unknown",
                    tool_name=tool_name,
                    confirmation_id=confirmation,
                    operation_ids=operation_ids,
                    applied_steps=applied,
                    failed_step=FailedStep(
                        index=index, operation_id=step.operation_id, error=str(exc)
                    ),
                    next_actions=[
                        "read current state to learn whether this step applied "
                        "before retrying anything by hand"
                    ],
                ),
            )
        if not 200 <= outcome.status_code < 300:
            failure = FailedStep(
                index=index,
                operation_id=step.operation_id,
                error=f"HTTP {outcome.status_code}",
                status_code=outcome.status_code,
            )
            state = "partial_failure" if applied else "failed"
            return (
                applied,
                outcomes,
                WriteResult(
                    state=state,
                    tool_name=tool_name,
                    confirmation_id=confirmation,
                    operation_ids=operation_ids,
                    applied_steps=applied,
                    failed_step=failure,
                ),
            )
        applied.append(
            AppliedStep(
                index=index,
                operation_id=step.operation_id,
                status_code=outcome.status_code,
                request_id=outcome.request_id,
            )
        )
        outcomes.append(outcome)
    return applied, outcomes, None


async def run_guarded_write(
    spec: GuardedWriteSpec,
    deps: WriteDeps,
    *,
    prepared: PreparedWrite,
    approval: Any,
) -> WriteResult:
    """The full gate lifecycle from an approval decision to a receipt."""
    confirmation = prepared.nonce[:12]
    operation_ids = [step.operation_id for step in prepared.plan.steps]

    def before_dispatch(*warnings: str, next_preview: bool = True) -> WriteResult:
        return WriteResult(
            state="failed_before_dispatch",
            tool_name=spec.tool_name,
            confirmation_id=confirmation,
            operation_ids=operation_ids,
            warnings=list(warnings),
            next_actions=(
                ["request a new preview before retrying this write"] if next_preview else []
            ),
        )

    if not is_approved(approval):
        await deps.gate.cancel(prepared)
        return WriteResult(
            state="rejected",
            tool_name=spec.tool_name,
            confirmation_id=confirmation,
            operation_ids=operation_ids,
        )
    try:
        permit = await deps.gate.consume(prepared)
    except WriteSafetyError as exc:
        return before_dispatch(str(exc), next_preview=False)
    try:
        spec.revalidate(permit.plan)
    except ValueError as exc:
        return before_dispatch(f"approved plan failed revalidation; no write was sent: {exc}")
    if spec.recheck is not None:
        try:
            current = await spec.recheck(permit.plan)
        except ClockifyError as exc:
            return before_dispatch(
                f"could not verify current state after approval; no write was sent: {exc}"
            )
        if current != permit.plan.preconditions:
            return before_dispatch("state changed after approval; no write was sent")
    executor = ControlledWriteExecutor(permit, deps.sender)
    applied, outcomes, failure = await _dispatch_steps(
        spec.tool_name, confirmation, operation_ids, permit.plan.steps, executor.dispatch
    )
    if failure is not None:
        return failure
    data: Any = outcomes[-1].data if outcomes else None
    state: WriteState = "succeeded"  # no reconciliation planned: response is authoritative
    if spec.reconcile is not None:
        reconciled, read_back = await spec.reconcile(permit.plan, outcomes)
        state = "reconciled" if reconciled else "succeeded_unreconciled"
        if read_back is not None:
            data = read_back
    return WriteResult(
        state=state,
        tool_name=spec.tool_name,
        confirmation_id=confirmation,
        operation_ids=operation_ids,
        applied_steps=applied,
        data=data,
        request_ids=[o.request_id for o in outcomes if o.request_id],
    )


async def run_routine_write(
    tool_name: str,
    plan: WritePlan,
    deps: WriteDeps,
    *,
    reconcile: ReconcileFn | None = None,
) -> WriteResult:
    """Routine tier: same compiled plan and dispatch tail, no approval gate."""
    operation_ids = [step.operation_id for step in plan.steps]
    for step in plan.steps:
        if not BY_ID[step.operation_id].semantics.mutates:
            raise WriteSafetyError("read operations may not dispatch through a write plan")

    async def dispatch(_index: int, step: WriteStep) -> StepOutcome:
        status_code, request_id, data = await deps.sender(step)
        return StepOutcome(status_code, request_id, data)

    applied, outcomes, failure = await _dispatch_steps(
        tool_name, "", operation_ids, plan.steps, dispatch
    )
    if failure is not None:
        return failure
    data: Any = outcomes[-1].data if outcomes else None
    state: WriteState = "succeeded"
    if reconcile is not None:
        reconciled, read_back = await reconcile(plan, outcomes)
        state = "reconciled" if reconciled else "succeeded_unreconciled"
        if read_back is not None:
            data = read_back
    return WriteResult(
        state=state,
        tool_name=tool_name,
        confirmation_id="",
        operation_ids=operation_ids,
        applied_steps=applied,
        data=data,
        request_ids=[o.request_id for o in outcomes if o.request_id],
    )
