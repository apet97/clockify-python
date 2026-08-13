"""Routine time-tracking workflows: start, stop, switch, log, fix, packages.

Business logic only. Every mutation goes through the injected ``RoutineRun``
callable (single attempt, never retried); reads come from the workflow read
capability. Name arguments accept an id or an exact name.
"""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from clockify_mcp.errors import ToolError
from clockify_mcp.read_capability import WorkflowReadClient
from clockify_mcp.receipt import ChangeSet, EntityRef, NextCall, Receipt, Warning_, success_receipt
from clockify_mcp.workflows._resolve import resolve_project, resolve_tag
from clockify_mcp.workflows._resolve import resolve_task as _resolve_task
from clockify_mcp.writes.state import WriteResult

# (operation_id, path_args, body, query) -> WriteResult
RoutineRun = Callable[..., Awaitable[WriteResult]]

DEMO_PREFIX = "DEMO-"


def now_utc() -> str:
    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _require_success(result: WriteResult, action: str) -> Any:
    if result.state not in ("succeeded", "reconciled"):
        failure = result.failed_step.error if result.failed_step else result.state
        raise ToolError(f"{action} failed: {failure}")
    return result.data


async def _entry_body(
    reads: WorkflowReadClient,
    workspace_id: str,
    *,
    description: str | None,
    project: str | None,
    task: str | None,
    tags: list[str] | None,
    billable: bool | None,
    start: str,
    end: str | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"start": start}
    if end is not None:
        body["end"] = end
    if description is not None:
        body["description"] = description
    if billable is not None:
        body["billable"] = billable
    if project is not None:
        project_id = await resolve_project(reads, project, workspace_id)
        body["projectId"] = project_id
        if task is not None:
            body["taskId"] = await _resolve_task(reads, task, project_id, workspace_id)
    elif task is not None:
        raise ToolError("task requires a project")
    if tags:
        body["tagIds"] = [await resolve_tag(reads, tag, workspace_id) for tag in tags]
    return body


def _entry_receipt(action: str, data: Any, *, next_calls: list[NextCall]) -> Receipt:
    entry_id = data.get("id") if isinstance(data, dict) else None
    return success_receipt(
        action,
        entity="time_entry",
        ids={"timeEntryId": entry_id} if entry_id else None,
        data=data,
        changed=ChangeSet(created=[EntityRef(type="time_entry", id=entry_id)])
        if entry_id
        else None,
        next_calls=next_calls,
    )


async def start_work(
    reads: WorkflowReadClient,
    run: RoutineRun,
    workspace_id: str,
    *,
    description: str | None = None,
    project: str | None = None,
    task: str | None = None,
    tags: list[str] | None = None,
    billable: bool | None = None,
    start: str | None = None,
) -> Receipt:
    resolved_start = start or now_utc()
    body = await _entry_body(
        reads,
        workspace_id,
        description=description,
        project=project,
        task=task,
        tags=tags,
        billable=billable,
        start=resolved_start,
        end=None,
    )
    result = await run("postWorkspacesWorkspaceIdTimeEntries", {"workspaceId": workspace_id}, body)
    data = _require_success(result, "start_work")
    receipt = _entry_receipt(
        "start_work",
        data,
        next_calls=[
            NextCall(tool="clockify_stop_work", reason="Stop this timer when done."),
            NextCall(tool="clockify_switch_work", reason="Switch to another task."),
        ],
    )
    if start is None:
        receipt.meta = {"startWasDefaulted": True, "resolvedStart": resolved_start}
    return receipt


async def stop_work(reads: WorkflowReadClient, run: RoutineRun, workspace_id: str) -> Receipt:
    me = await reads.users.me()
    end = now_utc()
    result = await run(
        "patchWorkspacesWorkspaceIdUserUserIdTimeEntries",
        {"workspaceId": workspace_id, "userId": me.id},
        {"end": end},
    )
    if result.state == "failed" and result.failed_step and result.failed_step.status_code == 404:
        return success_receipt("stop_work", data={"stopped": False, "reason": "no timer running"})
    data = _require_success(result, "stop_work")
    entry_id = data.get("id") if isinstance(data, dict) else None
    return success_receipt(
        "stop_work",
        entity="time_entry",
        ids={"timeEntryId": entry_id} if entry_id else None,
        data=data,
        changed=ChangeSet(updated=[EntityRef(type="time_entry", id=entry_id)])
        if entry_id
        else None,
    )


async def switch_work(
    reads: WorkflowReadClient,
    run: RoutineRun,
    workspace_id: str,
    *,
    description: str | None = None,
    project: str | None = None,
    task: str | None = None,
    tags: list[str] | None = None,
    billable: bool | None = None,
) -> Receipt:
    warnings: list[Warning_] = []
    stopped = await stop_work(reads, run, workspace_id)
    if not stopped.ok:
        warnings.append(Warning_(code="stop_failed", message="previous timer was not stopped"))
    receipt = await start_work(
        reads,
        run,
        workspace_id,
        description=description,
        project=project,
        task=task,
        tags=tags,
        billable=billable,
    )
    receipt.action = "switch_work"
    receipt.warnings = warnings + receipt.warnings
    if stopped.changed and receipt.changed:
        receipt.changed.updated = stopped.changed.updated
    return receipt


async def log_work(
    reads: WorkflowReadClient,
    run: RoutineRun,
    workspace_id: str,
    *,
    description: str | None = None,
    start: str | None = None,
    end: str | None = None,
    duration_seconds: int | None = None,
    project: str | None = None,
    task: str | None = None,
    tags: list[str] | None = None,
    billable: bool | None = None,
) -> Receipt:
    if start is not None and end is not None:
        resolved_start, resolved_end = start, end
    elif duration_seconds is not None:
        resolved_end = end or now_utc()
        end_moment = datetime.strptime(resolved_end, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        resolved_start = (end_moment - timedelta(seconds=duration_seconds)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    else:
        raise ToolError("pass start+end, or duration_seconds (with optional end)")
    body = await _entry_body(
        reads,
        workspace_id,
        description=description,
        project=project,
        task=task,
        tags=tags,
        billable=billable,
        start=resolved_start,
        end=resolved_end,
    )
    result = await run("postWorkspacesWorkspaceIdTimeEntries", {"workspaceId": workspace_id}, body)
    data = _require_success(result, "log_work")
    return _entry_receipt(
        "log_work",
        data,
        next_calls=[NextCall(tool="clockify_review_day", reason="Verify the day's entries.")],
    )


async def fix_entry(
    reads: WorkflowReadClient,
    run: RoutineRun,
    workspace_id: str,
    *,
    entry_id: str,
    description: str | None = None,
    start: str | None = None,
    end: str | None = None,
    project: str | None = None,
    task: str | None = None,
    tag_ids: list[str] | None = None,
    billable: bool | None = None,
) -> Receipt:
    current = await reads.time_entries.get(entry_id, workspace_id=workspace_id)
    interval = current.time_interval
    body: dict[str, Any] = {
        # PUT replaces the entry: re-send every current field, then override.
        "start": start or (interval.start if interval else None),
        "end": end or (interval.end if interval else None),
        "description": description if description is not None else current.description,
        "billable": billable if billable is not None else current.billable,
        "projectId": current.project_id,
        "taskId": current.task_id,
        # [] clears tags; None keeps the current set.
        "tagIds": tag_ids if tag_ids is not None else current.tag_ids,
    }
    if project is not None:
        project_id = await resolve_project(reads, project, workspace_id)
        body["projectId"] = project_id
        if task is not None:
            body["taskId"] = await _resolve_task(reads, task, project_id, workspace_id)
    body = {key: value for key, value in body.items() if value is not None}
    result = await run(
        "putWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
        {"workspaceId": workspace_id, "timeEntryId": entry_id},
        body,
    )
    data = _require_success(result, "fix_entry")
    entry_ref = EntityRef(type="time_entry", id=entry_id)
    return success_receipt(
        "fix_entry",
        entity="time_entry",
        ids={"timeEntryId": entry_id},
        data=data,
        changed=ChangeSet(updated=[entry_ref]),
    )


async def _find_by_exact_name(fetchable: Any, name: str, **kwargs: Any) -> Any | None:
    items = await fetchable(name=name, strict_name_search=True, page=1, page_size=50, **kwargs)
    for item in items:
        if getattr(item, "name", None) == name:
            return item
    return None


async def create_work_package(
    reads: WorkflowReadClient,
    run: RoutineRun,
    workspace_id: str,
    *,
    project: str,
    client: str | None = None,
    task: str | None = None,
    tag: str | None = None,
) -> Receipt:
    created: list[EntityRef] = []
    reused: list[EntityRef] = []

    async def upsert(
        kind: str, name: str, find: Any, create_op: str, body: dict[str, Any], path: dict[str, str]
    ) -> str:
        existing = await find
        if existing is not None:
            reused.append(EntityRef(type=kind, id=existing.id, name=name))
            return existing.id
        result = await run(create_op, path, body)
        data = _require_success(result, f"create {kind}")
        entity_id = data.get("id") if isinstance(data, dict) else None
        if not entity_id:
            raise ToolError(f"create {kind} returned no id")
        created.append(EntityRef(type=kind, id=entity_id, name=name))
        return entity_id

    workspace_path = {"workspaceId": workspace_id}
    client_id: str | None = None
    if client is not None:
        client_id = await upsert(
            "client",
            client,
            _find_by_exact_name(reads.clients.list, client, workspace_id=workspace_id),
            "postWorkspacesWorkspaceIdClients",
            {"name": client},
            workspace_path,
        )
    project_body: dict[str, Any] = {"name": project}
    if client_id:
        project_body["clientId"] = client_id
    project_id = await upsert(
        "project",
        project,
        _find_by_exact_name(reads.projects.list, project, workspace_id=workspace_id),
        "createProject",
        project_body,
        workspace_path,
    )
    ids: dict[str, str] = {"projectId": project_id}
    if client_id:
        ids["clientId"] = client_id
    if task is not None:

        def list_tasks(**kwargs: Any) -> Any:
            return reads.tasks.list(project_id, **kwargs)

        task_id = await upsert(
            "task",
            task,
            _find_by_exact_name(list_tasks, task, workspace_id=workspace_id),
            "addTaskOnProject",
            {"name": task},
            {"workspaceId": workspace_id, "projectId": project_id},
        )
        ids["taskId"] = task_id
    if tag is not None:
        tag_id = await upsert(
            "tag",
            tag,
            _find_by_exact_name(reads.tags.list, tag, workspace_id=workspace_id),
            "postWorkspacesWorkspaceIdTags",
            {"name": tag},
            workspace_path,
        )
        ids["tagId"] = tag_id
    return success_receipt(
        "create_work_package",
        entity="work_package",
        ids=ids,
        changed=ChangeSet(created=created, reused=reused),
        next_calls=[
            NextCall(
                tool="clockify_start_work",
                args={"project": project, **({"task": task} if task else {})},
                reason="Start tracking against the new package.",
            )
        ],
    )


async def demo_seed(
    reads: WorkflowReadClient,
    run: RoutineRun,
    workspace_id: str,
    *,
    run_id: str = "phase1",
) -> Receipt:
    prefix = f"{DEMO_PREFIX}{run_id}-"
    package = await create_work_package(
        reads,
        run,
        workspace_id,
        project=f"{prefix}project",
        client=f"{prefix}client",
        task=f"{prefix}task",
        tag=f"{prefix}tag",
    )
    assert package.ids is not None
    entry_body = {
        "start": "2026-01-05T09:00:00Z",
        "end": "2026-01-05T09:15:00Z",
        "description": f"{prefix}entry",
        "projectId": package.ids["projectId"],
        "taskId": package.ids.get("taskId"),
        "tagIds": [package.ids["tagId"]] if "tagId" in package.ids else None,
    }
    entry_body = {key: value for key, value in entry_body.items() if value is not None}
    result = await run(
        "postWorkspacesWorkspaceIdTimeEntries", {"workspaceId": workspace_id}, entry_body
    )
    data = _require_success(result, "demo_seed entry")
    entry_id = data.get("id") if isinstance(data, dict) else None
    changed = package.changed or ChangeSet()
    if entry_id:
        changed.created.append(EntityRef(type="time_entry", id=entry_id))
    return success_receipt(
        "demo_seed",
        entity="demo_data",
        ids=package.ids,
        data={"prefix": prefix},
        changed=changed,
        next_calls=[
            NextCall(
                tool="clockify_demo_cleanup",
                args={"prefix": prefix},
                reason="Remove everything this seed created.",
            )
        ],
    )
