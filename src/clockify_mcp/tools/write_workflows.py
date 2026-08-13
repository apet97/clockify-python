# pyright: reportUnusedFunction=false
"""Write workflows: routine daily tracking plus gated business composites.

Routine workflows execute directly (single attempt) and return the receipt
envelope; ambiguity in a name argument becomes a clarification receipt with
real candidates, never a guess. Guarded workflows compile ONE plan, pass the
sealed approval gate, and return the standard ``WriteResult``.
"""

from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.errors import ClockifyError
from clockify.models import (
    CreateRecurringAssignmentRequest,
    CreateTimeOffRequest,
    ExpenseCreateRequest,
    InvoiceCreateRequest,
    WebhookRequest,
)
from clockify_mcp.errors import ToolError
from clockify_mcp.read_capability import WorkflowReadClient
from clockify_mcp.receipt import Clarification, Receipt, error_receipt, success_receipt
from clockify_mcp.resolve import AmbiguousNameError
from clockify_mcp.webhook_url import assert_safe_webhook_url
from clockify_mcp.workflows import cleanup, tracking
from clockify_mcp.workflows._resolve import resolve_category, resolve_client, resolve_policy
from clockify_mcp.workflows._resolve import resolve_project as _resolve_project
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.plans import build_plan, build_step
from clockify_mcp.writes.runner import (
    GuardedWriteSpec,
    WriteApproval,
    WriteDeps,
    elicit_approval,
    run_guarded_write,
    run_routine_write,
)
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register_write_workflows(server: MCPServer, deps: WriteDeps) -> None:
    reads = WorkflowReadClient(deps.read_client)

    def workspace_of(workspace_id: str | None) -> str:
        resolved = workspace_id or reads.workspace_id
        if not resolved:
            raise ToolError(
                "workspace_id is required: pass it to the tool or set CLOCKIFY_WORKSPACE_ID"
            )
        return resolved

    def runner(tool_name: str) -> tracking.RoutineRun:
        async def run(
            operation_id: str,
            path_args: dict[str, str],
            body: Any = None,
            query: dict[str, Any] | None = None,
        ) -> WriteResult:
            step = build_step(operation_id, path_args=path_args, body=body, query=query)
            plan = build_plan(title=tool_name, summary=f"{tool_name} step", steps=(step,))
            return await run_routine_write(tool_name, plan, deps)

        return run

    def routine(action: str, work: Callable[[], Awaitable[Receipt]]) -> Awaitable[Receipt]:
        async def guarded_by_receipt() -> Receipt:
            try:
                return await work()
            except AmbiguousNameError as exc:
                return success_receipt(
                    action,
                    clarification=Clarification(
                        question=str(exc), field=exc.label, candidates=exc.candidates
                    ),
                )
            except (ToolError, ClockifyError) as exc:
                return error_receipt(action, exc)

        return guarded_by_receipt()

    @server.tool(name="clockify_start_work", annotations=tool_annotations("clockify_start_work"))
    async def clockify_start_work(
        description: str | None = None,
        project: str | None = None,
        task: str | None = None,
        tags: list[str] | None = None,
        billable: bool | None = None,
        start: str | None = None,
        workspace_id: str | None = None,
    ) -> Receipt:
        """Start a timer (or a timed entry from `start`); names resolve to ids."""
        return await routine(
            "start_work",
            lambda: tracking.start_work(
                reads,
                runner("clockify_start_work"),
                workspace_of(workspace_id),
                description=description,
                project=project,
                task=task,
                tags=tags,
                billable=billable,
                start=start,
            ),
        )

    @server.tool(name="clockify_stop_work", annotations=tool_annotations("clockify_stop_work"))
    async def clockify_stop_work(workspace_id: str | None = None) -> Receipt:
        """Stop the running timer; succeeds with stopped=false when none runs."""
        return await routine(
            "stop_work",
            lambda: tracking.stop_work(
                reads, runner("clockify_stop_work"), workspace_of(workspace_id)
            ),
        )

    @server.tool(name="clockify_switch_work", annotations=tool_annotations("clockify_switch_work"))
    async def clockify_switch_work(
        description: str | None = None,
        project: str | None = None,
        task: str | None = None,
        tags: list[str] | None = None,
        billable: bool | None = None,
        workspace_id: str | None = None,
    ) -> Receipt:
        """Stop the running timer (if any) and start a new one in one call."""
        return await routine(
            "switch_work",
            lambda: tracking.switch_work(
                reads,
                runner("clockify_switch_work"),
                workspace_of(workspace_id),
                description=description,
                project=project,
                task=task,
                tags=tags,
                billable=billable,
            ),
        )

    @server.tool(name="clockify_log_work", annotations=tool_annotations("clockify_log_work"))
    async def clockify_log_work(
        description: str | None = None,
        start: str | None = None,
        end: str | None = None,
        duration_seconds: int | None = None,
        project: str | None = None,
        task: str | None = None,
        tags: list[str] | None = None,
        billable: bool | None = None,
        workspace_id: str | None = None,
    ) -> Receipt:
        """Log a completed entry: start+end, or duration_seconds (+optional end)."""
        return await routine(
            "log_work",
            lambda: tracking.log_work(
                reads,
                runner("clockify_log_work"),
                workspace_of(workspace_id),
                description=description,
                start=start,
                end=end,
                duration_seconds=duration_seconds,
                project=project,
                task=task,
                tags=tags,
                billable=billable,
            ),
        )

    @server.tool(name="clockify_fix_entry", annotations=tool_annotations("clockify_fix_entry"))
    async def clockify_fix_entry(
        entry_id: str,
        description: str | None = None,
        start: str | None = None,
        end: str | None = None,
        project: str | None = None,
        task: str | None = None,
        tag_ids: list[str] | None = None,
        billable: bool | None = None,
        workspace_id: str | None = None,
    ) -> Receipt:
        """Fix one entry field-safely: re-reads it, then PUTs the merged entry."""
        return await routine(
            "fix_entry",
            lambda: tracking.fix_entry(
                reads,
                runner("clockify_fix_entry"),
                workspace_of(workspace_id),
                entry_id=entry_id,
                description=description,
                start=start,
                end=end,
                project=project,
                task=task,
                tag_ids=tag_ids,
                billable=billable,
            ),
        )

    @server.tool(
        name="clockify_create_work_package",
        annotations=tool_annotations("clockify_create_work_package"),
    )
    async def clockify_create_work_package(
        project: str,
        client: str | None = None,
        task: str | None = None,
        tag: str | None = None,
        workspace_id: str | None = None,
    ) -> Receipt:
        """Upsert client/project/task/tag by exact name; reuses what exists."""
        return await routine(
            "create_work_package",
            lambda: tracking.create_work_package(
                reads,
                runner("clockify_create_work_package"),
                workspace_of(workspace_id),
                project=project,
                client=client,
                task=task,
                tag=tag,
            ),
        )

    @server.tool(name="clockify_demo_seed", annotations=tool_annotations("clockify_demo_seed"))
    async def clockify_demo_seed(
        run_id: str = "phase1", workspace_id: str | None = None
    ) -> Receipt:
        """Seed a DEMO-<run_id>-prefixed client/project/task/tag plus one entry."""
        return await routine(
            "demo_seed",
            lambda: tracking.demo_seed(
                reads,
                runner("clockify_demo_seed"),
                workspace_of(workspace_id),
                run_id=run_id,
            ),
        )

    # ------------------------------------------------------------------ guarded

    invoice_op = GuardedOp(
        deps,
        tool_name="clockify_invoice_client_work",
        title="Create invoice for client",
        operation_id="addInvoice",
        body_model=InvoiceCreateRequest,
    )

    async def prepare_invoice(
        client: str,
        currency: str,
        number: str,
        issued_date: str,
        due_date: str,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        workspace = invoice_op.workspace(workspace_id)
        client_id = await resolve_client(reads, client, workspace)
        body = InvoiceCreateRequest.model_validate(
            {
                "clientId": client_id,
                "currency": currency,
                "number": number,
                "issuedDate": issued_date,
                "dueDate": due_date,
            }
        )
        return await invoice_op.prepare(
            arguments={
                "client": client,
                "currency": currency,
                "number": number,
                "issued_date": issued_date,
                "due_date": due_date,
                "workspace_id": workspace_id,
            },
            path_args={"workspaceId": workspace},
            body=body,
        )

    def ask_invoice(
        prepared: Annotated[PreparedWrite, Resolve(prepare_invoice)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_invoice_client_work",
        annotations=tool_annotations("clockify_invoice_client_work"),
    )
    async def clockify_invoice_client_work(
        client: str,
        currency: str,
        number: str,
        issued_date: str,
        due_date: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_invoice)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_invoice)],
    ) -> WriteResult:
        """Create an invoice for a client (name or id). Import items afterwards."""
        return await invoice_op.run(prepared, approval)

    expense_op = GuardedOp(
        deps,
        tool_name="clockify_record_expense",
        title="Record expense",
        operation_id="createExpense",
        body_model=ExpenseCreateRequest,
    )

    async def prepare_expense(
        category: str,
        amount: float,
        date: str,
        project: str | None = None,
        notes: str | None = None,
        billable: bool | None = None,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        workspace = expense_op.workspace(workspace_id)
        me = await reads.users.me()
        category_id = await resolve_category(reads, category, workspace)
        values: dict[str, Any] = {
            "userId": me.id,
            "categoryId": category_id,
            "amount": amount,
            "date": date,
        }
        if project is not None:
            values["projectId"] = await _resolve_project(reads, project, workspace)
        if notes is not None:
            values["notes"] = notes
        if billable is not None:
            values["billable"] = billable
        body = ExpenseCreateRequest.model_validate(values)
        return await expense_op.prepare(
            arguments={
                "category": category,
                "amount": amount,
                "date": date,
                "project": project,
                "notes": notes,
                "billable": billable,
                "workspace_id": workspace_id,
            },
            path_args={"workspaceId": workspace},
            body=body,
        )

    def ask_expense(
        prepared: Annotated[PreparedWrite, Resolve(prepare_expense)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_record_expense",
        annotations=tool_annotations("clockify_record_expense"),
    )
    async def clockify_record_expense(
        category: str,
        amount: float,
        date: str,
        project: str | None = None,
        notes: str | None = None,
        billable: bool | None = None,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_expense)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_expense)],
    ) -> WriteResult:
        """Record an expense for the current user. `amount` is in major units."""
        return await expense_op.run(prepared, approval)

    time_off_op = GuardedOp(
        deps,
        tool_name="clockify_request_time_off",
        title="Request time off",
        operation_id="createTimeOffRequest",
        body_model=CreateTimeOffRequest,
    )

    async def prepare_time_off(
        policy: str,
        start: str,
        end: str,
        note: str | None = None,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        workspace = time_off_op.workspace(workspace_id)
        policy_id = await resolve_policy(reads, policy, workspace)
        values: dict[str, Any] = {"timeOffPeriod": {"period": {"start": start, "end": end}}}
        if note is not None:
            values["note"] = note
        body = CreateTimeOffRequest.model_validate(values)
        return await time_off_op.prepare(
            arguments={
                "policy": policy,
                "start": start,
                "end": end,
                "note": note,
                "workspace_id": workspace_id,
            },
            path_args={"workspaceId": workspace, "policyId": policy_id},
            body=body,
        )

    def ask_time_off(
        prepared: Annotated[PreparedWrite, Resolve(prepare_time_off)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_request_time_off",
        annotations=tool_annotations("clockify_request_time_off"),
    )
    async def clockify_request_time_off(
        policy: str,
        start: str,
        end: str,
        note: str | None = None,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_time_off)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_time_off)],
    ) -> WriteResult:
        """Request time off under a policy (name or id)."""
        return await time_off_op.run(prepared, approval)

    schedule_op = GuardedOp(
        deps,
        tool_name="clockify_schedule_work",
        title="Schedule work",
        operation_id="createRecurringAssignment",
        body_model=CreateRecurringAssignmentRequest,
    )

    async def prepare_schedule(
        project: str,
        start: str,
        end: str,
        hours_per_day: float,
        user_id: str | None = None,
        note: str | None = None,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        workspace = schedule_op.workspace(workspace_id)
        project_id = await _resolve_project(reads, project, workspace)
        assignee = user_id or (await reads.users.me()).id
        values: dict[str, Any] = {
            "projectId": project_id,
            "userId": assignee,
            "start": start,
            "end": end,
            "hoursPerDay": hours_per_day,
        }
        if note is not None:
            values["note"] = note
        body = CreateRecurringAssignmentRequest.model_validate(values)
        return await schedule_op.prepare(
            arguments={
                "project": project,
                "start": start,
                "end": end,
                "hours_per_day": hours_per_day,
                "user_id": user_id,
                "note": note,
                "workspace_id": workspace_id,
            },
            path_args={"workspaceId": workspace},
            body=body,
        )

    def ask_schedule(
        prepared: Annotated[PreparedWrite, Resolve(prepare_schedule)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_schedule_work", annotations=tool_annotations("clockify_schedule_work")
    )
    async def clockify_schedule_work(
        project: str,
        start: str,
        end: str,
        hours_per_day: float,
        user_id: str | None = None,
        note: str | None = None,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_schedule)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_schedule)],
    ) -> WriteResult:
        """Schedule an assignment on a project (defaults to the current user)."""
        return await schedule_op.run(prepared, approval)

    webhook_op = GuardedOp(
        deps,
        tool_name="clockify_setup_webhook",
        title="Set up webhook",
        operation_id="createWebhook",
        body_model=WebhookRequest,
    )

    async def prepare_webhook(
        name: str,
        url: str,
        event: str,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        assert_safe_webhook_url(url)
        workspace = webhook_op.workspace(workspace_id)
        body = WebhookRequest.model_validate(
            {
                "name": name,
                "url": url,
                "webhookEvent": event,
                "triggerSource": [workspace],
                "triggerSourceType": "WORKSPACE_ID",
            }
        )
        return await webhook_op.prepare(
            arguments={
                "name": name,
                "url": url,
                "event": event,
                "workspace_id": workspace_id,
            },
            path_args={"workspaceId": workspace},
            body=body,
        )

    def ask_webhook(
        prepared: Annotated[PreparedWrite, Resolve(prepare_webhook)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_setup_webhook", annotations=tool_annotations("clockify_setup_webhook")
    )
    async def clockify_setup_webhook(
        name: str,
        url: str,
        event: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_webhook)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_webhook)],
    ) -> WriteResult:
        """Create a workspace-scoped webhook. The authToken is redacted."""
        result = await webhook_op.run(prepared, approval)
        if isinstance(result.data, dict) and "authToken" in result.data:
            result.data = {**result.data, "authToken": "[redacted]"}
        return result

    cleanup_spec = GuardedWriteSpec(
        tool_name="clockify_demo_cleanup",
        revalidate=cleanup.revalidate_cleanup,
    )

    async def prepare_cleanup(
        prefix: str = "DEMO-", workspace_id: str | None = None
    ) -> PreparedWrite:
        workspace = workspace_of(workspace_id)
        steps, preview = await cleanup.discover_cleanup_steps(reads, workspace, prefix)
        if not steps:
            raise ToolError(f"nothing to clean: no {prefix}* entities found")
        plan = cleanup.cleanup_plan(workspace, prefix, steps, preview)
        return await deps.gate.prepare(
            tool_name="clockify_demo_cleanup",
            arguments={"prefix": prefix, "workspace_id": workspace_id},
            workspace_id=workspace,
            plan=plan,
        )

    def ask_cleanup(
        prepared: Annotated[PreparedWrite, Resolve(prepare_cleanup)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_demo_cleanup", annotations=tool_annotations("clockify_demo_cleanup")
    )
    async def clockify_demo_cleanup(
        prefix: str = "DEMO-",
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_cleanup)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_cleanup)],
    ) -> WriteResult:
        """Delete every DEMO-/sdk-demo- prefixed entity under ONE approval."""
        cleanup.assert_demo_prefix(prefix)  # defense in depth beyond the gate
        return await run_guarded_write(cleanup_spec, deps, prepared=prepared, approval=approval)
