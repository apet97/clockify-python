"""Result states and the structured write receipt."""

from typing import Any, Literal

from pydantic import BaseModel

WriteState = Literal[
    "rejected",
    "expired",
    "failed_before_dispatch",
    "failed",
    "outcome_unknown",
    "partial_failure",
    "succeeded",
    "succeeded_unreconciled",
    "reconciled",
]


class AppliedStep(BaseModel):
    index: int
    operation_id: str
    status_code: int
    request_id: str | None = None


class FailedStep(BaseModel):
    index: int
    operation_id: str
    error: str
    status_code: int | None = None


class WriteResult(BaseModel):
    state: WriteState
    tool_name: str
    confirmation_id: str
    operation_ids: list[str]
    applied_steps: list[AppliedStep] = []
    failed_step: FailedStep | None = None
    data: Any = None
    warnings: list[str] = []
    next_actions: list[str] = []
    request_ids: list[str] = []
