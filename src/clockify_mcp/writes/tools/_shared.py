"""Shared helpers for write tools.

``GuardedOp`` wires one operation to the sealed gate: it compiles the exact
plan at prepare time, renders the deterministic preview, and runs the shared
lifecycle. ``RoutineOp`` compiles the same plan shape but executes directly —
single attempt, never retried. The tier comes from ``RISK_BY_TOOL``; using
the wrong helper for a tool's tier fails at registration, not at runtime.
"""

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ValidationError

from clockify.operations.model import ReplacementSemantics
from clockify.operations.registry import BY_ID
from clockify_mcp.errors import ToolError
from clockify_mcp.risk import GUARDED_RISKS, RISK_BY_TOOL, Risk, annotations_for
from clockify_mcp.writes.plan import PreparedWrite, WritePlan
from clockify_mcp.writes.plans import build_plan, build_step, make_revalidator, preview_fields_from
from clockify_mcp.writes.runner import (
    GuardedWriteSpec,
    WriteDeps,
    run_guarded_write,
    run_routine_write,
)
from clockify_mcp.writes.state import WriteResult

_REPLACE_WARNING = (
    "PUT replacement: omitted fields may be cleared on the server. "
    "Read the current entity first and send every field you want to keep."
)


def tool_annotations(tool_name: str):  # type: ignore[no-untyped-def]
    """Annotations from the risk map; unclassified tools fail at import."""
    return annotations_for(RISK_BY_TOOL[tool_name])


def _validated_body(body: Any, model: type[BaseModel] | None) -> Any:
    if body is None or model is None:
        return body
    if isinstance(body, model):
        return body
    try:
        return model.model_validate(body)
    except ValidationError as exc:
        raise ToolError(f"invalid body: {exc}") from exc


def _plain(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(by_alias=True, exclude_none=True)
    return value


class _OpBase:
    def __init__(
        self,
        deps: WriteDeps,
        *,
        tool_name: str,
        title: str,
        operation_id: str,
        body_model: type[BaseModel] | None = None,
    ) -> None:
        self.deps = deps
        self.tool_name = tool_name
        self.title = title
        self.operation_id = operation_id
        self.body_model = body_model

    def workspace(self, workspace_id: str | None) -> str:
        resolved = workspace_id or self.deps.read_client.workspace_id
        if not resolved:
            raise ToolError(
                "workspace_id is required: pass it to the tool or set CLOCKIFY_WORKSPACE_ID"
            )
        return resolved

    def _build_plan(
        self,
        *,
        path_args: Mapping[str, str],
        body: Any,
        query: Mapping[str, Any] | None,
        summary: str | None,
        scope: str,
    ) -> WritePlan:
        operation = BY_ID[self.operation_id]
        warnings: tuple[str, ...] = ()
        if operation.semantics.replacement in (
            ReplacementSemantics.FULL_REPLACE_PROVEN,
            ReplacementSemantics.MIXED_PROVEN,
            ReplacementSemantics.UNKNOWN_CONSERVATIVE,
        ):
            warnings = (_REPLACE_WARNING,)
        step = build_step(self.operation_id, path_args=path_args, body=body, query=query)
        return build_plan(
            title=self.title,
            summary=summary or f"{self.title}: {operation.http_method} {operation.path}",
            steps=(step,),
            scope=scope,
            preview_fields=preview_fields_from(body),
            warnings=warnings,
        )


class GuardedOp(_OpBase):
    """One guarded write tool over one operation."""

    def __init__(
        self,
        deps: WriteDeps,
        *,
        tool_name: str,
        title: str,
        operation_id: str,
        body_model: type[BaseModel] | None = None,
    ) -> None:
        super().__init__(
            deps,
            tool_name=tool_name,
            title=title,
            operation_id=operation_id,
            body_model=body_model,
        )
        if RISK_BY_TOOL[tool_name] not in GUARDED_RISKS:
            raise ValueError(f"{tool_name} is not a guarded tier; use RoutineOp")
        self.spec = GuardedWriteSpec(
            tool_name=tool_name,
            revalidate=make_revalidator(
                (operation_id,),
                body_models={operation_id: body_model} if body_model else None,
            ),
        )

    async def prepare(
        self,
        *,
        arguments: dict[str, Any],
        path_args: Mapping[str, str],
        body: Any = None,
        query: Mapping[str, Any] | None = None,
        summary: str | None = None,
        scope: str = "one entity",
    ) -> PreparedWrite:
        validated = _validated_body(body, self.body_model)
        plan = self._build_plan(
            path_args=path_args, body=validated, query=query, summary=summary, scope=scope
        )
        return await self.deps.gate.prepare(
            tool_name=self.tool_name,
            arguments={key: _plain(value) for key, value in arguments.items()},
            workspace_id=path_args.get("workspaceId"),
            plan=plan,
        )

    async def run(self, prepared: PreparedWrite, approval: Any) -> WriteResult:
        return await run_guarded_write(self.spec, self.deps, prepared=prepared, approval=approval)


class RoutineOp(_OpBase):
    """One routine-tier write tool: no approval round trip, single attempt."""

    def __init__(
        self,
        deps: WriteDeps,
        *,
        tool_name: str,
        title: str,
        operation_id: str,
        body_model: type[BaseModel] | None = None,
    ) -> None:
        super().__init__(
            deps,
            tool_name=tool_name,
            title=title,
            operation_id=operation_id,
            body_model=body_model,
        )
        if RISK_BY_TOOL[tool_name] is not Risk.ROUTINE_WRITE:
            raise ValueError(f"{tool_name} is not routine tier; use GuardedOp")

    async def execute(
        self,
        *,
        path_args: Mapping[str, str],
        body: Any = None,
        query: Mapping[str, Any] | None = None,
        summary: str | None = None,
    ) -> WriteResult:
        validated = _validated_body(body, self.body_model)
        plan = self._build_plan(
            path_args=path_args, body=validated, query=query, summary=summary, scope="one entity"
        )
        return await run_routine_write(self.tool_name, plan, self.deps)
