# pyright: reportUnusedFunction=false
"""Orientation tools: static guidance plus registry-backed operation lookup.

None of these tools touches the network or the configured credential, so they
work before setup. `clockify_operation_guide` answers from the live operation
registry — it cannot drift from the actual surface.
"""

from typing import Any

from mcp.server import MCPServer

from clockify.operations.registry import ALL_OPERATIONS
from clockify_mcp.risk import RISK_BY_TOOL
from clockify_mcp.tools._shared import READ_ANNOTATIONS

TOOLS_GUIDE: dict[str, Any] = {
    "start_here": [
        "clockify_status shows the current user, workspace, and running timer.",
        "clockify_doctor diagnoses credential and workspace configuration.",
        "clockify_workspace_overview summarizes the pinned workspace.",
    ],
    "tool_groups": {
        "reads": "clockify_<resource>_<list|get|filter> tools mirror the Clockify API.",
        "reports": "clockify_reports_* generate summary/detailed/weekly/attendance reports.",
        "reviews": "clockify_review_day and clockify_review_week audit a time window.",
        "writes": "clockify_<resource>_<create|update|delete|...> tools mutate data.",
        "workflows": "clockify_start_work/stop_work/log_work compose common tasks.",
    },
    "write_doctrine": [
        "Routine writes (personal time entries) execute directly and are never retried.",
        "Guarded writes show the user a preview of the exact request; the user "
        "approves or rejects it out of band. The model never sees or supplies "
        "the approval.",
        "A rejected or expired approval means no request was sent. Ask again "
        "with a fresh call if the user still wants the change.",
        "PUT updates replace the whole entity: read it first and send every "
        "field you want to keep.",
        "Deletes are not reversible; archive prerequisites apply to projects, "
        "clients (archive first), and tasks (mark DONE first).",
    ],
    "rules_of_thumb": [
        "Prefer workflows over raw tools for multi-step intents.",
        "Use ids from previous results instead of re-resolving names.",
        "Pass workspace_id only to override the pinned workspace.",
    ],
}

PLAN_CHANGE_INTENTS: dict[str, list[dict[str, Any]]] = {
    "track time": [
        {"tool": "clockify_start_work", "mutates": True, "requires_approval": False},
        {"tool": "clockify_stop_work", "mutates": True, "requires_approval": False},
    ],
    "log past work": [
        {"tool": "clockify_log_work", "mutates": True, "requires_approval": False},
    ],
    "fix an entry": [
        {"tool": "clockify_review_day", "mutates": False, "requires_approval": False},
        {"tool": "clockify_fix_entry", "mutates": True, "requires_approval": False},
    ],
    "set up a project": [
        {"tool": "clockify_create_work_package", "mutates": True, "requires_approval": False},
    ],
    "invoice a client": [
        {"tool": "clockify_invoice_client_work", "mutates": True, "requires_approval": True},
    ],
    "record an expense": [
        {"tool": "clockify_record_expense", "mutates": True, "requires_approval": True},
    ],
    "request time off": [
        {"tool": "clockify_request_time_off", "mutates": True, "requires_approval": True},
    ],
    "schedule work": [
        {"tool": "clockify_schedule_work", "mutates": True, "requires_approval": True},
    ],
    "set up a webhook": [
        {"tool": "clockify_setup_webhook", "mutates": True, "requires_approval": True},
    ],
    "clean up demo data": [
        {"tool": "clockify_demo_cleanup", "mutates": True, "requires_approval": True},
    ],
}

SDK_SNIPPETS: dict[str, str] = {
    "install": 'uv add "clockify-python-115[mcp]"',
    "client": (
        "from clockify import ClockifyClient\n"
        "async with ClockifyClient(api_key=..., workspace_id=...) as client:\n"
        "    me = await client.users.me()"
    ),
    "list_time_entries": (
        "entries = await client.time_entries.list_for_user(\n"
        "    user_id=me.id, start='2026-08-01T00:00:00Z', end='2026-08-08T00:00:00Z')"
    ),
    "report": (
        "report = await client.reports.summary(body={\n"
        "    'dateRangeStart': start, 'dateRangeEnd': end,\n"
        "    'summaryFilter': {'groups': ['PROJECT']}})"
    ),
    "create_tag": "tag = await client.tags.create(body={'name': 'deep-work'})",
}


def register_orientation(server: MCPServer) -> None:
    @server.tool(name="clockify_tools_guide", annotations=READ_ANNOTATIONS)
    async def clockify_tools_guide() -> dict[str, Any]:
        """How this server's tools fit together. Static; works before setup."""
        return TOOLS_GUIDE

    @server.tool(name="clockify_plan_change", annotations=READ_ANNOTATIONS)
    async def clockify_plan_change(intent: str) -> dict[str, Any]:
        """Map an intent (e.g. 'track time', 'invoice a client') to a tool chain."""
        wanted = intent.strip().casefold()
        matches = {
            name: steps
            for name, steps in PLAN_CHANGE_INTENTS.items()
            if wanted in name or name in wanted
        }
        if not matches:
            return {
                "intent": intent,
                "plan": [],
                "known_intents": sorted(PLAN_CHANGE_INTENTS),
                "note": "no matching intent; pick one of known_intents or use raw tools",
            }
        return {"intent": intent, "plans": matches}

    @server.tool(name="clockify_operation_guide", annotations=READ_ANNOTATIONS)
    async def clockify_operation_guide(query: str, limit: int = 8) -> dict[str, Any]:
        """Search the 168-operation registry by id, path, resource, or method."""
        wanted = query.strip().casefold()
        scored: list[tuple[int, dict[str, Any]]] = []
        for operation in ALL_OPERATIONS:
            haystacks = (
                operation.operation_id.casefold(),
                operation.path.casefold(),
                operation.resource.casefold(),
                operation.sdk_method.casefold(),
            )
            score = sum(3 if wanted == hay else 1 for hay in haystacks if wanted in hay)
            if score:
                tool_name = f"clockify_{operation.resource}_{operation.sdk_method}"
                scored.append(
                    (
                        score,
                        {
                            "operation_id": operation.operation_id,
                            "method": operation.http_method,
                            "path": operation.path,
                            "resource": operation.resource,
                            "sdk_method": f"client.{operation.resource}.{operation.sdk_method}",
                            "mutates": operation.semantics.mutates,
                            "effect": operation.semantics.effect.value,
                            "mcp_tool": tool_name if tool_name in RISK_BY_TOOL else None,
                        },
                    )
                )
        scored.sort(key=lambda item: (-item[0], item[1]["operation_id"]))
        return {"query": query, "operations": [entry for _, entry in scored[:limit]]}

    @server.tool(name="clockify_sdk_snippet", annotations=READ_ANNOTATIONS)
    async def clockify_sdk_snippet(topic: str | None = None) -> dict[str, Any]:
        """Python SDK snippets: install, client, list_time_entries, report, create_tag."""
        if topic and topic in SDK_SNIPPETS:
            return {"topic": topic, "snippet": SDK_SNIPPETS[topic]}
        return {"topics": sorted(SDK_SNIPPETS), "snippets": SDK_SNIPPETS}
