# pyright: reportUnusedFunction=false
"""Wave-1 write adapter: `clockify_tags_create` (Safety Phase G exemplar).

Single-entity, additive, reversible, direct read-back, no multipart — the
simplest write that satisfies Safety Phase G. Later waves follow this exact
pattern, one reviewed tool at a time.

Nothing here is registered by the shipped read-only server. `build_approved_server`
exists for gate testing and target-host compatibility evaluation only; the ship
conditions in docs/port/MCP_WRITE_SAFETY_PLAN.md (independent human review, two
real host approval-UI proofs) remain unmet, so no release registers it.
"""

import json
from typing import Annotated, Any, Literal

import httpx
from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve
from mcp.server.request_state import RequestStateSecurity
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from clockify._transport.auth import Credential
from clockify._transport.executor import HttpExecutor
from clockify.client import ClockifyClient
from clockify.config import DEFAULT_TIMEOUT
from clockify.errors import ClockifyAPIError, ClockifyError
from clockify.operations.registry import BY_ID
from clockify_mcp.context import ServerConfig, build_read_only_client
from clockify_mcp.errors import ToolError, to_tool_error
from clockify_mcp.tools import register_read_tools
from clockify_mcp.tools.workflows import register_workflows
from clockify_mcp.writes.canonical import canonical_json
from clockify_mcp.writes.executor import ControlledWriteExecutor
from clockify_mcp.writes.gate import WriteGate, fingerprint_state, is_approved
from clockify_mcp.writes.nonce_store import WriteSafetyError
from clockify_mcp.writes.plan import (
    Precondition,
    PreparedWrite,
    PreviewField,
    ReconciliationPlan,
    WritePlan,
    WriteStep,
    render_preview,
)
from clockify_mcp.writes.principal import AUDIENCE, new_process_secret
from clockify_mcp.writes.reconcile import reconcile
from clockify_mcp.writes.state import AppliedStep, FailedStep, WriteResult

WRITE_ANNOTATIONS = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,  # additive create; hints are never the boundary
    idempotent_hint=False,
    open_world_hint=True,
)


class WriteApproval(BaseModel):
    decision: Literal["approve", "reject"]


def _approved_tag_target(plan: WritePlan) -> tuple[str, str]:
    """Extract the final read target only from the consumed, stored plan."""
    if len(plan.steps) != 1:
        raise ValueError("approved tag plan must contain exactly one step")
    step = plan.steps[0]
    if (
        step.operation_id != "postWorkspacesWorkspaceIdTags"
        or len(step.path_arguments) != 1
        or step.path_arguments[0][0] != "workspaceId"
        or not step.path_arguments[0][1]
        or step.query
        or step.multipart_fields
        or step.files
        or step.body_json is None
    ):
        raise ValueError("approved tag plan has an invalid request shape")
    body = json.loads(step.body_json)
    if not isinstance(body, dict) or set(body) != {"name"} or not isinstance(body["name"], str):
        raise ValueError("approved tag plan has an invalid body")
    return step.path_arguments[0][1], body["name"]


def make_step_sender(write_executor: HttpExecutor):  # type: ignore[no-untyped-def]
    """Adapt a WriteStep to one real dispatch through the normal transport."""

    async def send(step: WriteStep) -> tuple[int, str | None, Any]:
        operation = BY_ID[step.operation_id]
        body = json.loads(step.body_json) if step.body_json is not None else None
        response = await write_executor.execute(
            operation,
            path_args=dict(step.path_arguments),
            query=dict(step.query) or None,
            body=body,
        )
        return response.status_code, response.request_id, response.data

    return send


def register_tags_create(
    server: MCPServer,
    *,
    read_client: ClockifyClient,
    gate: WriteGate,
    write_executor: HttpExecutor,
) -> None:
    sender = make_step_sender(write_executor)

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

    async def prepare_write(name: str, workspace_id: str | None = None) -> PreparedWrite:
        resolved = workspace_id or read_client.workspace_id
        if not resolved:
            raise ToolError("workspace_id is required")
        if not name or len(name) > 100:
            raise ToolError("tag name must be 1-100 characters")
        # Read-only current-state check: is the name already taken?
        try:
            exact, preconditions = await read_name_preconditions(name, resolved)
        except ClockifyError as exc:
            raise to_tool_error(exc) from exc
        if exact:
            raise ToolError(f"a tag named {name!r} already exists (id {exact[0].id})")
        plan = WritePlan(
            version=1,
            title="Create tag",
            summary=f"Create tag {name!r} in workspace {resolved}",
            effect="create",
            scope="one entity",
            sensitivity=(),
            reversibility="reversible (delete removes it; the name stays reserved)",
            steps=(
                WriteStep(
                    operation_id="postWorkspacesWorkspaceIdTags",
                    path_arguments=(("workspaceId", resolved),),
                    body_json=canonical_json({"name": name}),
                ),
            ),
            preconditions=preconditions,
            preview_fields=(PreviewField("name", name),),
            reconciliation=ReconciliationPlan(
                kind="direct_get",
                description="GET the created tag by returned id",
                operation_id="getWorkspacesWorkspaceIdTagsTagId",
            ),
        )
        return await gate.prepare(
            tool_name="clockify_tags_create",
            arguments={"name": name, "workspace_id": workspace_id},
            workspace_id=resolved,
            plan=plan,
        )

    def ask_for_approval(
        prepared: Annotated[PreparedWrite, Resolve(prepare_write)],
    ) -> Elicit[WriteApproval]:
        return Elicit(message=render_preview(prepared), schema=WriteApproval)

    @server.tool(name="clockify_tags_create", annotations=WRITE_ANNOTATIONS)
    async def clockify_tags_create(
        name: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_write)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_for_approval)],
    ) -> WriteResult:
        """Create a workspace tag after explicit user approval of the exact request."""
        confirmation = prepared.nonce[:12]
        operation_ids = [s.operation_id for s in prepared.plan.steps]
        if not is_approved(approval):
            await gate.cancel(prepared)
            return WriteResult(
                state="rejected",
                tool_name="clockify_tags_create",
                confirmation_id=confirmation,
                operation_ids=operation_ids,
            )
        try:
            permit = await gate.consume(prepared)
        except WriteSafetyError as exc:
            return WriteResult(
                state="failed_before_dispatch",
                tool_name="clockify_tags_create",
                confirmation_id=confirmation,
                operation_ids=operation_ids,
                warnings=[str(exc)],
            )
        try:
            approved_workspace_id, approved_name = _approved_tag_target(permit.plan)
        except ValueError:
            return WriteResult(
                state="failed_before_dispatch",
                tool_name="clockify_tags_create",
                confirmation_id=confirmation,
                operation_ids=operation_ids,
                warnings=["approved plan has an invalid tag request; no write was sent"],
                next_actions=["request a new preview before trying to create this tag"],
            )
        try:
            _, current_preconditions = await read_name_preconditions(
                approved_name, approved_workspace_id
            )
        except ClockifyError as exc:
            return WriteResult(
                state="failed_before_dispatch",
                tool_name="clockify_tags_create",
                confirmation_id=confirmation,
                operation_ids=operation_ids,
                warnings=[
                    "could not verify tag state after approval; no write was sent: "
                    f"{to_tool_error(exc)}"
                ],
                next_actions=["request a new preview before trying to create this tag"],
            )
        if current_preconditions != permit.plan.preconditions:
            return WriteResult(
                state="failed_before_dispatch",
                tool_name="clockify_tags_create",
                confirmation_id=confirmation,
                operation_ids=operation_ids,
                warnings=["tag state changed after approval; no write was sent"],
                next_actions=["request a new preview before trying to create this tag"],
            )
        executor = ControlledWriteExecutor(permit, sender)
        step = permit.plan.steps[0]
        try:
            outcome = await executor.dispatch(0, step)
        except ClockifyAPIError as exc:
            return WriteResult(
                state="failed",
                tool_name="clockify_tags_create",
                confirmation_id=confirmation,
                operation_ids=operation_ids,
                failed_step=FailedStep(
                    index=0,
                    operation_id=step.operation_id,
                    error=str(exc),
                    status_code=exc.status_code,
                ),
            )
        except ClockifyError as exc:
            return WriteResult(
                state="outcome_unknown",
                tool_name="clockify_tags_create",
                confirmation_id=confirmation,
                operation_ids=operation_ids,
                failed_step=FailedStep(index=0, operation_id=step.operation_id, error=str(exc)),
                next_actions=[
                    "list tags filtered by the requested name to learn whether the "
                    "tag was created before retrying by hand"
                ],
            )
        applied = [
            AppliedStep(
                index=0,
                operation_id=step.operation_id,
                status_code=outcome.status_code,
                request_id=outcome.request_id,
            )
        ]
        created_id = outcome.data.get("id") if isinstance(outcome.data, dict) else None
        assert permit.plan.reconciliation is not None
        if created_id and prepared.workspace_id:
            read_back_plan = ReconciliationPlan(
                kind="direct_get",
                description=permit.plan.reconciliation.description,
                operation_id=permit.plan.reconciliation.operation_id,
                path_arguments=(
                    ("workspaceId", prepared.workspace_id),
                    ("tagId", created_id),
                ),
            )
            reconciled, data = await reconcile(read_client, read_back_plan)
        else:
            reconciled, data = False, None
        return WriteResult(
            state="reconciled" if reconciled else "succeeded_unreconciled",
            tool_name="clockify_tags_create",
            confirmation_id=confirmation,
            operation_ids=operation_ids,
            applied_steps=applied,
            data=data if data is not None else outcome.data,
            request_ids=[r for r in (outcome.request_id,) if r],
        )


def build_approved_server(
    config: ServerConfig | None = None,
    *,
    read_client: ClockifyClient | None = None,
    write_http_client: httpx.AsyncClient | None = None,
) -> MCPServer:
    """Full-mode server: all read tools plus the reviewed wave-1 write tool.

    NOT the shipped default. `clockify-mcp` always builds the read-only server;
    this constructor exists for gate testing and target-host compatibility
    evaluation until every write ship condition is proven.
    """
    resolved_config = config or ServerConfig.from_env()
    resolved_config.require_credential()
    if read_client is None:
        read_client = build_read_only_client(resolved_config)
    credential = Credential(
        api_key=resolved_config.api_key, addon_token=resolved_config.addon_token
    )
    process_secret = new_process_secret()
    gate = WriteGate(process_secret=process_secret, credential=credential)
    write_executor = HttpExecutor(
        client=write_http_client or httpx.AsyncClient(timeout=DEFAULT_TIMEOUT),
        credential=credential,
    )
    security = RequestStateSecurity(
        keys=[process_secret],
        ttl=300.0,
        bind_principal=lambda _ctx: gate.principal_id,
        audience=AUDIENCE,
    )
    server = MCPServer(
        name="clockify-full",
        instructions=(
            "Clockify tools including ONE gated write (clockify_tags_create). "
            "Every write requires explicit user approval of the exact request."
        ),
        log_level="WARNING",
        request_state_security=security,
    )
    register_read_tools(server, read_client)
    register_workflows(server, read_client, resolved_config)
    register_tags_create(server, read_client=read_client, gate=gate, write_executor=write_executor)
    return server
