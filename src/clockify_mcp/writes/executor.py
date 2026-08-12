"""ControlledWriteExecutor: only a consumed permit's exact ordered steps dispatch.

The sender is injected (real HttpExecutor in production, a mock in tests); the
gate below is identical either way. Nothing here retries a mutation.
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from clockify.operations.registry import BY_ID
from clockify_mcp.writes.nonce_store import ExecutionPermit, WriteSafetyError
from clockify_mcp.writes.plan import WriteStep

# The sender receives the recompiled step and returns (status_code, request_id, data).
StepSender = Callable[[WriteStep], Awaitable[tuple[int, str | None, Any]]]


class PermitViolation(WriteSafetyError):
    pass


class StepOutcome:
    __slots__ = ("data", "request_id", "status_code")

    def __init__(self, status_code: int, request_id: str | None, data: Any) -> None:
        self.status_code = status_code
        self.request_id = request_id
        self.data = data


class ControlledWriteExecutor:
    """Tracks the next allowed step; terminal after completion or any failure."""

    def __init__(self, permit: ExecutionPermit, sender: StepSender) -> None:
        self._permit = permit
        self._sender = sender
        self._next_index = 0
        self._terminal = False

    @property
    def next_index(self) -> int:
        return self._next_index

    @property
    def terminal(self) -> bool:
        return self._terminal

    def _validate(self, step_index: int, step: WriteStep) -> None:
        # Principal and tool identity are bound at WriteGate.consume (the permit
        # cannot exist otherwise); destination service is inside request_digest
        # and final-host validation still runs below the gate in the transport
        # (review finding E — defence-in-depth note, not an enforcement gap).
        if self._terminal:
            raise PermitViolation("permit is terminal; no further step may dispatch")
        if step_index != self._next_index:
            raise PermitViolation(
                f"step {step_index} is not the next allowed step ({self._next_index})"
            )
        if step_index >= len(self._permit.plan.steps):
            raise PermitViolation("step index beyond the approved plan")
        approved = self._permit.plan.steps[step_index]
        if step.operation_id != approved.operation_id:
            self._terminal = True
            raise PermitViolation(
                f"operation {step.operation_id!r} was not approved for step {step_index}"
            )
        operation = BY_ID.get(step.operation_id)
        if operation is None:
            self._terminal = True
            raise PermitViolation(f"unknown operation {step.operation_id!r}")
        if not operation.semantics.mutates:
            self._terminal = True
            raise PermitViolation("read operations may not use a write permit")
        # Recompiled digest must equal the approved digest byte-for-byte.
        if step.request_digest != approved.request_digest:
            self._terminal = True
            raise PermitViolation(
                "dispatched request differs from the approved plan "
                f"(step {step_index}); approval does not transfer"
            )

    async def dispatch(self, step_index: int, step: WriteStep) -> StepOutcome:
        """Dispatch exactly the approved step. Any ambiguity is terminal."""
        self._validate(step_index, step)
        # Review finding X: send the permit's stored step object, never the
        # caller's, so the gate does not depend on request_digest covering every
        # current and future WriteStep field.
        approved_step = self._permit.plan.steps[step_index]
        try:
            status_code, request_id, data = await self._sender(approved_step)
        except asyncio.CancelledError:
            self._terminal = True
            raise
        except (httpx.TransportError, Exception):
            self._terminal = True
            raise
        if not 200 <= status_code < 300:
            self._terminal = True
            return StepOutcome(status_code, request_id, data)
        self._next_index += 1
        if self._next_index >= len(self._permit.plan.steps):
            self._terminal = True
        return StepOutcome(status_code, request_id, data)
