"""`clockify_review_day` and `clockify_review_week`.

Both use explicit wall-clock windows in a caller-supplied IANA timezone,
because Clockify evaluates several ranges as wall-clock values.
"""

from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from clockify.errors import ClockifyError
from clockify_mcp.errors import ToolError, to_tool_error
from clockify_mcp.read_capability import WorkflowReadClient

_PAGE_SIZE = 200
_MAX_PAGES = 5  # bounded pagination; the result flags truncation


def _window(day: date, days: int, timezone_name: str) -> tuple[str, str]:
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ToolError(f"unknown timezone {timezone_name!r} (use an IANA name)") from exc
    start = datetime.combine(day, time.min, tzinfo=zone)
    end = start + timedelta(days=days)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return (
        start.astimezone(ZoneInfo("UTC")).strftime(fmt),
        end.astimezone(ZoneInfo("UTC")).strftime(fmt),
    )


def _parse_date(value: str, field: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ToolError(f"{field} must be an ISO date (YYYY-MM-DD), got {value!r}") from exc
    if value != parsed.isoformat():
        raise ToolError(f"{field} must be an ISO date (YYYY-MM-DD), got {value!r}")
    return parsed


async def _entries_between(
    client: WorkflowReadClient, workspace_id: str, user_id: str, start: str, end: str
) -> tuple[list[dict[str, Any]], bool]:
    entries: list[dict[str, Any]] = []
    truncated = False
    for page in range(1, _MAX_PAGES + 1):
        batch = await client.time_entries.list_for_user(
            user_id,
            workspace_id=workspace_id,
            start=start,
            end=end,
            page=page,
            page_size=_PAGE_SIZE,
        )
        for entry in batch:
            interval = entry.time_interval
            entries.append(
                {
                    "id": entry.id,
                    "description": entry.description,
                    "projectId": entry.project_id,
                    "taskId": entry.task_id,
                    "start": interval.start if interval else None,
                    "end": interval.end if interval else None,
                    "duration": interval.duration if interval else None,
                }
            )
        if len(batch) < _PAGE_SIZE:
            break
    else:
        truncated = True
    return entries, truncated


async def _resolve_scope(
    client: WorkflowReadClient, workspace_id: str | None, user_id: str | None
) -> tuple[str, str]:
    resolved_workspace = workspace_id or client.workspace_id
    if user_id is None or resolved_workspace is None:
        me = await client.users.me()
        user_id = user_id or me.id
        resolved_workspace = resolved_workspace or me.default_workspace or me.active_workspace
    if not resolved_workspace:
        raise ToolError("no workspace_id configured and the user has no default workspace")
    if not user_id:
        raise ToolError("could not resolve a user id")
    return resolved_workspace, user_id


async def review_day(
    client: WorkflowReadClient,
    day: str,
    *,
    timezone_name: str = "UTC",
    user_id: str | None = None,
    workspace_id: str | None = None,
    correlate_projects: bool = False,
) -> dict[str, Any]:
    parsed = _parse_date(day, "day")
    start, end = _window(parsed, 1, timezone_name)
    try:
        workspace, user = await _resolve_scope(client, workspace_id, user_id)
        entries, truncated = await _entries_between(client, workspace, user, start, end)
        projects: dict[str, str] = {}
        if correlate_projects:
            project_ids = {e["projectId"] for e in entries if e["projectId"]}
            for project_id in sorted(project_ids):
                project = await client.projects.get(project_id, workspace_id=workspace)
                projects[project_id] = project.name or project_id
    except ClockifyError as exc:
        raise to_tool_error(exc) from exc
    result: dict[str, Any] = {
        "day": day,
        "timezone": timezone_name,
        "window": {"start": start, "end": end},
        "userId": user,
        "entries": entries,
        "entry_count": len(entries),
        "truncated": truncated,
    }
    if correlate_projects:
        result["projects"] = projects
    return result


async def review_week(
    client: WorkflowReadClient,
    start_day: str,
    *,
    timezone_name: str = "UTC",
    user_id: str | None = None,
    workspace_id: str | None = None,
) -> dict[str, Any]:
    """Exactly seven days from start_day; the weekly report demands this interval."""
    parsed = _parse_date(start_day, "start_day")
    start, end = _window(parsed, 7, timezone_name)
    try:
        workspace, user = await _resolve_scope(client, workspace_id, user_id)
        entries, truncated = await _entries_between(client, workspace, user, start, end)
        summary = await client.reports.weekly(
            {
                "dateRangeStart": start,
                "dateRangeEnd": end,
                "users": {"ids": [user], "contains": "CONTAINS", "status": "ALL"},
                "weeklyFilter": {"group": "USER", "subgroup": "TIME"},
            },
            workspace_id=workspace,
        )
        totals = summary.totals if hasattr(summary, "totals") else None
    except ClockifyError as exc:
        raise to_tool_error(exc) from exc
    return {
        "start_day": start_day,
        "timezone": timezone_name,
        "window": {"start": start, "end": end, "days": 7},
        "userId": user,
        "entries": entries,
        "entry_count": len(entries),
        "truncated": truncated,
        "report_totals": (
            [t.model_dump(by_alias=True) if t is not None else None for t in totals]
            if totals
            else None
        ),
    }
