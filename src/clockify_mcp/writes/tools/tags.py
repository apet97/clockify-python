# pyright: reportUnusedFunction=false
"""Guarded write tools: tags."""

import json
from typing import Annotated, Any

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.errors import ClockifyError
from clockify.models import TagCreate
from clockify_mcp.errors import ToolError, to_tool_error
from clockify_mcp.risk import Risk, annotations_for
from clockify_mcp.writes.executor import StepOutcome
from clockify_mcp.writes.gate import fingerprint_state
from clockify_mcp.writes.plan import Precondition, PreparedWrite, ReconciliationPlan, WritePlan
from clockify_mcp.writes.plans import build_plan, build_step, make_revalidator, preview_fields_from
from clockify_mcp.writes.reconcile import reconcile
from clockify_mcp.writes.runner import (
    GuardedWriteSpec,
    WriteApproval,
    WriteDeps,
    elicit_approval,
    run_guarded_write,
)
from clockify_mcp.writes.state import WriteResult

_CREATE_OP = "postWorkspacesWorkspaceIdTags"


def register(server: MCPServer, deps: WriteDeps) -> None:
    read_client = deps.read_client

    async def read_name_preconditions(
        name: str, workspace_id: str
    ) -> tuple[list[Any], tuple[Precondition, ...]]:
        existing = await read_client.tags.list(
            workspace_id=workspace_id,
            name=name,
            strict_name_search=True,
            page=1,
            page_size=1,
        )
        exact = [tag for tag in existing if tag.name == name]
        return exact, (
            Precondition(
                f"no tag named {name!r} exists",
                fingerprint_state({"names": sorted(tag.name or "" for tag in exact)}),
            ),
        )

    async def prepare_create(name: str, workspace_id: str | None = None) -> PreparedWrite:
        resolved = workspace_id or read_client.workspace_id
        if not resolved:
            raise ToolError("workspace_id is required")
        if not name or len(name) > 100:
            raise ToolError("tag name must be 1-100 characters")
        try:
            exact, preconditions = await read_name_preconditions(name, resolved)
        except ClockifyError as exc:
            raise to_tool_error(exc) from exc
        if exact:
            raise ToolError(f"a tag named {name!r} already exists (id {exact[0].id})")
        body = {"name": name}
        plan = build_plan(
            title="Create tag",
            summary=f"Create tag {name!r} in workspace {resolved}",
            steps=(build_step(_CREATE_OP, path_args={"workspaceId": resolved}, body=body),),
            preconditions=preconditions,
            preview_fields=preview_fields_from(body),
            reconciliation=ReconciliationPlan(
                kind="direct_get",
                description="GET the created tag by returned id",
                operation_id="getWorkspacesWorkspaceIdTagsTagId",
            ),
        )
        return await deps.gate.prepare(
            tool_name="clockify_tags_create",
            arguments={"name": name, "workspace_id": workspace_id},
            workspace_id=resolved,
            plan=plan,
        )

    def ask_create(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    async def recheck(plan: WritePlan) -> tuple[Precondition, ...]:
        step = plan.steps[0]
        assert step.body_json is not None
        name = json.loads(step.body_json)["name"]
        workspace_id = dict(step.path_arguments)["workspaceId"]
        _, preconditions = await read_name_preconditions(name, workspace_id)
        return preconditions

    async def reconcile_create(plan: WritePlan, outcomes: list[StepOutcome]) -> tuple[bool, Any]:
        data = outcomes[-1].data
        created_id = data.get("id") if isinstance(data, dict) else None
        if not created_id:
            return False, None
        workspace_id = dict(plan.steps[0].path_arguments)["workspaceId"]
        assert plan.reconciliation is not None
        return await reconcile(
            read_client,
            ReconciliationPlan(
                kind="direct_get",
                description=plan.reconciliation.description,
                operation_id=plan.reconciliation.operation_id,
                path_arguments=(("workspaceId", workspace_id), ("tagId", created_id)),
            ),
        )

    create_spec = GuardedWriteSpec(
        tool_name="clockify_tags_create",
        revalidate=make_revalidator((_CREATE_OP,), body_models={_CREATE_OP: TagCreate}),
        recheck=recheck,
        reconcile=reconcile_create,
    )

    @server.tool(name="clockify_tags_create", annotations=annotations_for(Risk.BUSINESS_WRITE))
    async def clockify_tags_create(
        name: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a workspace tag after explicit user approval of the exact request."""
        return await run_guarded_write(create_spec, deps, prepared=prepared, approval=approval)
