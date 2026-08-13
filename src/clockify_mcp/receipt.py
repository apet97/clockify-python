"""Uniform receipt envelope for write tools and workflows.

Read tools keep their existing ``ReadResult`` shape; writes and workflows
return this richer envelope so agents can chain calls: ``ids`` and ``changed``
carry every entity reference, ``next`` suggests the follow-up call, and
``clarification`` turns name ambiguity into a grounded question instead of a
guess. Failures carry a stable ``error.code`` plus a concrete recovery hint.
"""

from typing import Any

from pydantic import BaseModel

from clockify_mcp.error_codes import classify_error, is_retryable, recovery_hint


class EntityRef(BaseModel):
    type: str
    id: str
    name: str | None = None


class ChangeSet(BaseModel):
    created: list[EntityRef] = []
    updated: list[EntityRef] = []
    deleted: list[EntityRef] = []
    reused: list[EntityRef] = []


class Clarification(BaseModel):
    question: str
    field: str
    candidates: list[EntityRef]


class NextCall(BaseModel):
    tool: str
    args: dict[str, Any] | None = None
    reason: str | None = None


class Warning_(BaseModel):
    code: str | None = None
    message: str


class ErrorInfo(BaseModel):
    code: str
    message: str


class Recovery(BaseModel):
    hint: str
    tool: str | None = None
    args: dict[str, Any] | None = None
    retryable: bool = False


class Receipt(BaseModel):
    ok: bool
    action: str
    entity: str | None = None
    ids: dict[str, str] | None = None
    data: Any = None
    meta: dict[str, Any] | None = None
    changed: ChangeSet | None = None
    warnings: list[Warning_] = []
    clarification: Clarification | None = None
    next: list[NextCall] = []
    error: ErrorInfo | None = None
    recovery: Recovery | None = None


def success_receipt(
    action: str,
    *,
    entity: str | None = None,
    ids: dict[str, str] | None = None,
    data: Any = None,
    meta: dict[str, Any] | None = None,
    changed: ChangeSet | None = None,
    warnings: list[Warning_] | None = None,
    clarification: Clarification | None = None,
    next_calls: list[NextCall] | None = None,
) -> Receipt:
    return Receipt(
        ok=True,
        action=action,
        entity=entity,
        ids=ids,
        data=data,
        meta=meta,
        changed=changed,
        warnings=warnings or [],
        clarification=clarification,
        next=next_calls or [],
    )


def error_receipt(
    action: str,
    exc: BaseException,
    *,
    hint: str | None = None,
    tool: str | None = None,
    args: dict[str, Any] | None = None,
) -> Receipt:
    code = classify_error(exc)
    return Receipt(
        ok=False,
        action=action,
        error=ErrorInfo(code=code, message=str(exc)),
        recovery=Recovery(
            hint=hint or recovery_hint(code),
            tool=tool,
            args=args,
            retryable=is_retryable(code),
        ),
    )
