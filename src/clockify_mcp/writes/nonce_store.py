"""Bounded in-memory nonce store: atomic issue, reuse, invalidate, consume.

Request-state integrity (the official SDK boundary) proves a confirmation is
genuine; only this store makes it single-use. Consumption happens BEFORE the
first mutation dispatch and is never rolled back.
"""

import asyncio
import hmac
import secrets
import time
from dataclasses import dataclass

from clockify_mcp.writes.plan import PreparedWrite, WritePlan


class WriteSafetyError(Exception):
    """Base class for every deliberate write-gate refusal."""


class NonceStoreError(WriteSafetyError):
    """Base class for store refusals; message states the exact reason."""


class ConfirmationExpired(NonceStoreError):
    pass


class ConfirmationAlreadyUsed(NonceStoreError):
    pass


class ConfirmationNotFound(NonceStoreError):
    pass


class ConfirmationMismatch(NonceStoreError):
    pass


class StoreAtCapacity(NonceStoreError):
    pass


class PlanTooLarge(NonceStoreError):
    pass


@dataclass(frozen=True, slots=True)
class ExecutionPermit:
    permit_id: str
    principal_id: str
    tool_name: str
    arguments_digest: str
    plan: WritePlan
    consumed_at: float


class InMemoryNonceStore:
    """Process-local. A restart drops all pending state — safe stdio behavior."""

    def __init__(
        self,
        *,
        ttl: float = 300.0,
        max_pending: int = 128,
        max_plan_bytes: int = 256 * 1024,
        clock: "callable | None" = None,  # type: ignore[type-arg]
    ) -> None:
        self._ttl = ttl
        self._max_pending = max_pending
        self._max_plan_bytes = max_plan_bytes
        self._clock = clock or time.monotonic
        self._lock = asyncio.Lock()
        self._pending: dict[str, PreparedWrite] = {}  # key -> record
        self._by_nonce: dict[str, str] = {}  # nonce -> key
        self._tombstones: dict[str, tuple[str, float]] = {}  # nonce -> (principal, expiry)

    def _now(self) -> float:
        return float(self._clock())

    def _prune(self) -> None:
        now = self._now()
        for key, record in list(self._pending.items()):
            if record.expires_at <= now:
                self._by_nonce.pop(record.nonce, None)
                del self._pending[key]
        for nonce, (_, expiry) in list(self._tombstones.items()):
            if expiry <= now:
                del self._tombstones[nonce]

    def _plan_size(self, plan: WritePlan) -> int:
        """Byte size of everything the record retains (review finding A: every
        stored string counts, or the 256 KiB cap is bypassable via warnings/
        summary/preconditions)."""
        total = 0
        for step in plan.steps:
            if step.body_json is not None:
                total += len(step.body_json)
            total += sum(len(k) + len(v) for k, v in step.path_arguments)
            total += sum(len(k) + len(v) for k, v in step.query)
            total += sum(len(k) + len(v) for k, v in step.multipart_fields)
            for file_digest in step.files:
                total += (
                    len(file_digest.field_name)
                    + len(file_digest.filename)
                    + len(file_digest.content_type)
                    + len(file_digest.sha256)
                )
        for preview_field in plan.preview_fields:
            total += len(preview_field.label) + len(preview_field.value)
        total += len(plan.title) + len(plan.summary) + len(plan.effect)
        total += len(plan.scope) + len(plan.reversibility)
        total += sum(len(s) for s in plan.sensitivity)
        total += sum(len(w) for w in plan.warnings)
        for precondition in plan.preconditions:
            total += len(precondition.description) + len(precondition.fingerprint)
        return total

    async def get_or_issue(
        self,
        *,
        key: str,
        principal_id: str,
        tool_name: str,
        workspace_id: str | None,
        arguments_digest: str,
        plan: WritePlan,
    ) -> PreparedWrite:
        """Atomic: same pending key + same plan digest returns the same nonce."""
        async with self._lock:
            self._prune()
            plan_digest = plan.digest
            existing = self._pending.get(key)
            if existing is not None:
                if existing.plan_digest == plan_digest:
                    # Review finding B: the reuse branch must not trust `key`
                    # alone — every caller binding must match the stored record.
                    bindings_match = (
                        hmac.compare_digest(existing.principal_id, principal_id)
                        and existing.tool_name == tool_name
                        and existing.workspace_id == workspace_id
                        and hmac.compare_digest(existing.arguments_digest, arguments_digest)
                    )
                    if not bindings_match:
                        raise ConfirmationMismatch(
                            "pending confirmation key collision with different bindings"
                        )
                    return existing
                # Current state changed the plan: old approval must not carry over.
                self._by_nonce.pop(existing.nonce, None)
                del self._pending[key]
            if self._plan_size(plan) > self._max_plan_bytes:
                raise PlanTooLarge(f"canonical plan exceeds {self._max_plan_bytes} bytes")
            if len(self._pending) >= self._max_pending:
                raise StoreAtCapacity(
                    f"{self._max_pending} confirmations already pending; retry later"
                )
            now = self._now()
            record = PreparedWrite(
                key=key,
                nonce=secrets.token_urlsafe(32),
                principal_id=principal_id,
                tool_name=tool_name,
                workspace_id=workspace_id,
                arguments_digest=arguments_digest,
                plan=plan,
                plan_digest=plan_digest,
                issued_at=now,
                expires_at=now + self._ttl,
            )
            self._pending[key] = record
            self._by_nonce[record.nonce] = key
            return record

    async def cancel(self, nonce: str) -> None:
        async with self._lock:
            key = self._by_nonce.pop(nonce, None)
            if key is not None:
                self._pending.pop(key, None)

    async def consume(
        self,
        *,
        nonce: str,
        principal_id: str,
        tool_name: str,
        workspace_id: str | None,
        arguments_digest: str,
        plan_digest: str,
    ) -> ExecutionPermit:
        """Atomic single-use. Never restores the nonce after a later failure."""
        async with self._lock:
            self._prune()
            if nonce in self._tombstones:
                raise ConfirmationAlreadyUsed("confirmation_already_used")
            key = self._by_nonce.get(nonce)
            if key is None:
                raise ConfirmationNotFound(
                    "confirmation not found: expired, cancelled, or never issued"
                )
            record = self._pending[key]
            if record.expires_at <= self._now():
                self._by_nonce.pop(nonce, None)
                del self._pending[key]
                raise ConfirmationExpired("confirmation expired; request a new preview")
            checks = (
                hmac.compare_digest(record.principal_id, principal_id),
                hmac.compare_digest(record.tool_name, tool_name),
                record.workspace_id == workspace_id,  # F2: consume-time workspace binding
                hmac.compare_digest(record.arguments_digest, arguments_digest),
                hmac.compare_digest(record.plan_digest, plan_digest),
            )
            if not all(checks):
                raise ConfirmationMismatch(
                    "confirmation does not match this principal/tool/workspace/arguments/plan"
                )
            del self._pending[key]
            self._by_nonce.pop(nonce, None)
            self._tombstones[nonce] = (principal_id, record.expires_at)
            return ExecutionPermit(
                permit_id=secrets.token_urlsafe(16),
                principal_id=principal_id,
                tool_name=tool_name,
                arguments_digest=arguments_digest,
                plan=record.plan,
                consumed_at=self._now(),
            )

    async def pending_count(self) -> int:
        async with self._lock:
            self._prune()
            return len(self._pending)
