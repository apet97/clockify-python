"""Data-driven plan construction and consumed-plan revalidation.

Plans are compiled from the operation registry: the effect class, replacement
semantics, and lifecycle prerequisites all come from the ``Operation`` record,
so a write tool describes intent (which operation, which arguments) and this
module produces the exact bound wire plan plus the revalidator that re-checks
the consumed plan's shape before dispatch.
"""

import json
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ValidationError

from clockify.operations.model import MutationEffect
from clockify.operations.registry import BY_ID
from clockify_mcp.writes.canonical import canonical_json
from clockify_mcp.writes.plan import (
    Precondition,
    PreviewField,
    ReconciliationPlan,
    WritePlan,
    WriteStep,
)
from clockify_mcp.writes.runner import RevalidateFn

BULK_SOFT_CAP = 100
BULK_HARD_CAP = 1000

_EFFECT_REVERSIBILITY = {
    MutationEffect.CREATE: "reversible (the created entity can be deleted)",
    MutationEffect.REPLACE: "overwrites every field; prior values are not recoverable",
    MutationEffect.PATCH: "changes only the listed fields",
    MutationEffect.TRANSITION: "state transition; reversing may need another transition",
    MutationEffect.DELETE: "NOT reversible",
    MutationEffect.BULK: "affects many entities at once",
}


def build_step(
    operation_id: str,
    *,
    path_args: Mapping[str, str],
    body: Any = None,
    query: Mapping[str, Any] | None = None,
) -> WriteStep:
    """Compile one exact wire step; body is canonicalized at bind time.

    Query keys are the operation's Python parameter names (the transport maps
    them to wire names); list values become repeated pairs so exploded
    parameters survive the round trip through the stored step.
    """
    operation = BY_ID[operation_id]
    missing = [name for name in operation.path_parameters if not path_args.get(name)]
    if missing:
        raise ValueError(f"{operation_id} requires path arguments: {', '.join(missing)}")
    if isinstance(body, BaseModel):
        body = body.model_dump(by_alias=True, exclude_none=True)
    pairs: list[tuple[str, str]] = []
    for key in sorted(query or {}):
        value = (query or {})[key]
        if isinstance(value, (list, tuple)):
            pairs.extend((key, str(item)) for item in value)
        elif value is not None:
            pairs.append((key, str(value)))
    return WriteStep(
        operation_id=operation_id,
        path_arguments=tuple((name, path_args[name]) for name in operation.path_parameters),
        query=tuple(pairs),
        body_json=canonical_json(body) if body is not None else None,
    )


def preview_fields_from(body: Any) -> tuple[PreviewField, ...]:
    """Flat preview of the bound body's top-level fields."""
    if isinstance(body, BaseModel):
        body = body.model_dump(by_alias=True, exclude_none=True)
    if not isinstance(body, dict):
        return ()
    return tuple(
        PreviewField(str(key), json.dumps(value, sort_keys=True, default=str))
        for key, value in sorted(body.items())
    )


def build_plan(
    *,
    title: str,
    summary: str,
    steps: tuple[WriteStep, ...],
    scope: str = "one entity",
    sensitivity: tuple[str, ...] = (),
    preconditions: tuple[Precondition, ...] = (),
    preview_fields: tuple[PreviewField, ...] = (),
    warnings: tuple[str, ...] = (),
    reconciliation: ReconciliationPlan | None = None,
) -> WritePlan:
    """Assemble a plan; effect and reversibility come from the final step."""
    effect = BY_ID[steps[-1].operation_id].semantics.effect
    return WritePlan(
        version=1,
        title=title,
        summary=summary,
        effect=effect.value,
        scope=scope,
        sensitivity=sensitivity,
        reversibility=_EFFECT_REVERSIBILITY[effect],
        steps=steps,
        preconditions=preconditions,
        preview_fields=preview_fields,
        warnings=warnings,
        reconciliation=reconciliation,
    )


def make_revalidator(
    expected_operations: tuple[str, ...],
    *,
    body_models: Mapping[str, type[BaseModel]] | None = None,
) -> RevalidateFn:
    """Shape-check a consumed plan: operations, path args, and body validity.

    The revalidator never trusts tool arguments — only the stored plan the
    nonce was consumed for. A body model re-rejects unknown fields exactly as
    the SDK request model does at prepare time.
    """

    def revalidate(plan: WritePlan) -> None:
        actual = tuple(step.operation_id for step in plan.steps)
        if actual != expected_operations:
            raise ValueError(f"plan operations {actual} != approved shape {expected_operations}")
        for step in plan.steps:
            operation = BY_ID[step.operation_id]
            bound = dict(step.path_arguments)
            if set(bound) != set(operation.path_parameters) or not all(bound.values()):
                raise ValueError(f"step {step.operation_id} has invalid path arguments")
            if step.multipart_fields or step.files:
                raise ValueError("multipart writes are not exposed through MCP")
            if step.body_json is not None:
                try:
                    body = json.loads(step.body_json)
                except ValueError as exc:
                    raise ValueError(f"step {step.operation_id} body is not JSON") from exc
                if not isinstance(body, (dict, list)):
                    raise ValueError(f"step {step.operation_id} body must be an object or array")
                model = (body_models or {}).get(step.operation_id)
                if model is not None:
                    try:
                        model.model_validate(body)
                    except ValidationError as exc:
                        raise ValueError(
                            f"step {step.operation_id} body failed model validation: {exc}"
                        ) from exc

    return revalidate


def enforce_bulk_caps(ids: tuple[str, ...]) -> tuple[str, ...]:
    """Canonical sorted ID set with the bulk caps: warn-worthy above the soft
    cap is the caller's concern; above the hard cap the plan refuses to build."""
    unique = tuple(sorted(set(ids)))
    if len(unique) > BULK_HARD_CAP:
        raise ValueError(f"bulk write of {len(unique)} ids exceeds the {BULK_HARD_CAP} cap")
    return unique
