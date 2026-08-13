# pyright: reportPrivateUsage=false, reportMissingParameterType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportAttributeAccessIssue=false
"""Write workflows through the full server with a mock Clockify backend."""

import json as jsonlib
from typing import Any

import httpx
import pytest
from mcp.types import CallToolResult, ElicitResult, TextContent

from clockify_mcp.context import ServerConfig
from clockify_mcp.full_server import build_full_server
from mcp import Client

from .conftest import MockBackend, make_mock_client

WORKSPACE = "w-test"
ME = {"id": "u" * 24, "name": "Test User", "email": "t@example.com", "status": "ACTIVE"}


def _project(project_id: str, name: str) -> dict[str, Any]:
    return {
        "id": project_id,
        "name": name,
        "workspaceId": WORKSPACE,
        "archived": False,
        "billable": True,
        "color": "#000000",
        "public": False,
        "template": False,
    }


PROJECT = _project("p" * 24, "Internal")
DEMO_PROJECT = _project("d" * 24, "DEMO-x-project")
ENTRY = {
    "id": "e" * 24,
    "description": "old words",
    "billable": True,
    "isLocked": False,
    "type": "REGULAR",
    "userId": "u" * 24,
    "workspaceId": WORKSPACE,
    "projectId": PROJECT["id"],
    "tagIds": ["t" * 24],
    "timeInterval": {"start": "2026-08-13T08:00:00Z", "end": "2026-08-13T09:00:00Z"},
}
CONFIG = ServerConfig(api_key="test-key", addon_token=None, workspace_id=WORKSPACE)


class WorkflowBackend(MockBackend):
    """Read fixtures plus a mutation recorder."""

    def __init__(self, *, running_timer: bool = True, demo: bool = False) -> None:
        super().__init__()
        self.mutations: list[httpx.Request] = []
        self.running_timer = running_timer
        self.demo = demo

        def responder(request: httpx.Request) -> httpx.Response:
            path = request.url.path
            if request.method in ("POST", "PUT", "PATCH", "DELETE"):
                self.mutations.append(request)
                if path.endswith("/user") is False and "time-entries" in path:
                    if request.method == "PATCH" and not self.running_timer:
                        return httpx.Response(404, json={"message": "no timer"})
                    return httpx.Response(200, json={"id": "new-entry"})
                return httpx.Response(200, json={"id": "created-id"})
            if path.endswith("/user"):
                return httpx.Response(200, json=ME)
            if path.endswith(f"/time-entries/{ENTRY['id']}"):
                return httpx.Response(200, json=ENTRY)
            if "/tasks" in path or "/tags" in path or "/clients" in path:
                return httpx.Response(200, json=[])
            if "/projects" in path and self.demo:
                return httpx.Response(200, json=[DEMO_PROJECT])
            if "/projects" in path:
                return httpx.Response(200, json=[PROJECT])
            if "time-entries" in path:
                return httpx.Response(200, json=[])
            return httpx.Response(200, json=[])

        self.responder = responder


def make_server(backend: WorkflowBackend):  # type: ignore[no-untyped-def]
    return build_full_server(
        CONFIG,
        read_client=make_mock_client(backend),
        write_http_client=httpx.AsyncClient(transport=httpx.MockTransport(backend.handler)),
    )


def payload_of(result: CallToolResult) -> dict[str, Any]:
    if isinstance(result.structured_content, dict):
        return result.structured_content
    first = result.content[0]
    assert isinstance(first, TextContent)
    assert not result.is_error, first.text
    return jsonlib.loads(first.text)


async def approve(context: Any, params: Any) -> ElicitResult:
    return ElicitResult(action="accept", content={"decision": "approve"})


async def call(backend: WorkflowBackend, tool: str, args: dict[str, Any]) -> dict[str, Any]:
    async with Client(make_server(backend), elicitation_callback=approve) as client:
        return payload_of(await client.call_tool(tool, args))


async def test_start_work_resolves_project_and_defaults_start() -> None:
    backend = WorkflowBackend()
    payload = await call(backend, "clockify_start_work", {"project": "Internal"})
    assert payload["ok"] is True, payload.get("error")
    assert payload["meta"]["startWasDefaulted"] is True
    body = jsonlib.loads(backend.mutations[0].content)
    assert body["projectId"] == PROJECT["id"]


async def test_stop_work_without_timer_is_ok_not_error() -> None:
    backend = WorkflowBackend(running_timer=False)
    payload = await call(backend, "clockify_stop_work", {})
    assert payload["ok"] is True, payload.get("error")
    assert payload["data"] == {"stopped": False, "reason": "no timer running"}


async def test_log_work_requires_a_time_shape() -> None:
    backend = WorkflowBackend()
    payload = await call(backend, "clockify_log_work", {"description": "x"})
    assert payload["ok"] is False
    assert "duration_seconds" in payload["error"]["message"]
    assert backend.mutations == []


async def test_fix_entry_re_reads_and_puts_merged_fields() -> None:
    backend = WorkflowBackend()
    payload = await call(
        backend, "clockify_fix_entry", {"entry_id": ENTRY["id"], "description": "new words"}
    )
    assert payload["ok"] is True, payload.get("error")
    body = jsonlib.loads(backend.mutations[0].content)
    assert body["description"] == "new words"
    # untouched fields re-sent (PUT-replace safety)
    assert body["projectId"] == PROJECT["id"]
    assert body["tagIds"] == ENTRY["tagIds"]
    assert body["start"] == "2026-08-13T08:00:00Z"


async def test_create_work_package_reuses_existing_project() -> None:
    backend = WorkflowBackend()
    payload = await call(backend, "clockify_create_work_package", {"project": "Internal"})
    assert payload["ok"] is True, payload.get("error")
    assert payload["changed"]["reused"][0]["id"] == PROJECT["id"]
    assert backend.mutations == []  # nothing needed creating


async def test_ambiguous_project_name_returns_clarification() -> None:
    backend = WorkflowBackend()
    dup = _project("q" * 24, "internal")

    original = backend.responder

    def responder(request: httpx.Request) -> httpx.Response:
        if "/projects" in request.url.path and request.method == "GET":
            return httpx.Response(200, json=[PROJECT, dup])
        return original(request)

    backend.responder = responder
    payload = await call(backend, "clockify_start_work", {"project": "internal"})
    assert payload["ok"] is True, payload.get("error")
    candidates = {c["id"] for c in payload["clarification"]["candidates"]}
    assert candidates == {PROJECT["id"], dup["id"]}
    assert backend.mutations == []


async def test_setup_webhook_refuses_unsafe_url_before_any_preview() -> None:
    backend = WorkflowBackend()
    async with Client(make_server(backend), elicitation_callback=approve) as client:
        result = await client.call_tool(
            "clockify_setup_webhook",
            {"name": "hook", "url": "https://169.254.169.254/x", "event": "NEW_TIME_ENTRY"},
        )
    assert result.is_error
    assert backend.mutations == []


async def test_record_expense_resolves_and_dispatches_once_after_approval() -> None:
    backend = WorkflowBackend()
    category = {"id": "c" * 24, "name": "Travel"}

    original = backend.responder

    def responder(request: httpx.Request) -> httpx.Response:
        if "/expenses/categories" in request.url.path and request.method == "GET":
            return httpx.Response(200, json={"categories": [category], "count": 1})
        return original(request)

    backend.responder = responder
    payload = await call(
        backend,
        "clockify_record_expense",
        {"category": "Travel", "amount": 12.5, "date": "2026-08-13"},
    )
    assert payload["state"] == "succeeded"
    expense_posts = [m for m in backend.mutations if m.url.path.endswith("/expenses")]
    assert len(expense_posts) == 1


async def test_demo_cleanup_refuses_non_demo_prefix() -> None:
    backend = WorkflowBackend(demo=True)
    async with Client(make_server(backend), elicitation_callback=approve) as client:
        result = await client.call_tool("clockify_demo_cleanup", {"prefix": "Internal"})
    assert result.is_error
    assert backend.mutations == []


async def test_demo_cleanup_archives_then_deletes_under_one_approval() -> None:
    backend = WorkflowBackend(demo=True)
    payload = await call(backend, "clockify_demo_cleanup", {"prefix": "DEMO-"})
    assert payload["state"] == "succeeded"
    ops = [(m.method, m.url.path) for m in backend.mutations]
    assert ops == [
        ("PUT", f"/api/v1/workspaces/{WORKSPACE}/projects/{DEMO_PROJECT['id']}"),
        ("DELETE", f"/api/v1/workspaces/{WORKSPACE}/projects/{DEMO_PROJECT['id']}"),
    ]
    archived_body = jsonlib.loads(backend.mutations[0].content)
    assert archived_body["archived"] is True


async def test_demo_cleanup_with_nothing_to_clean_is_an_error_before_preview() -> None:
    backend = WorkflowBackend(demo=False)

    original = backend.responder

    def responder(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and "/projects" in request.url.path:
            return httpx.Response(200, json=[])
        return original(request)

    backend.responder = responder
    async with Client(make_server(backend), elicitation_callback=approve) as client:
        result = await client.call_tool("clockify_demo_cleanup", {"prefix": "DEMO-"})
    assert result.is_error
    assert backend.mutations == []


@pytest.mark.parametrize(
    "tool",
    ["clockify_invoice_client_work", "clockify_request_time_off", "clockify_schedule_work"],
)
async def test_guarded_workflows_reject_without_dispatch(tool: str) -> None:
    backend = WorkflowBackend()
    policy = {"id": "y" * 24, "name": "Vacation"}

    original = backend.responder

    def responder(request: httpx.Request) -> httpx.Response:
        if "/time-off/policies" in request.url.path and request.method == "GET":
            return httpx.Response(200, json=[policy])
        if "/clients" in request.url.path and request.method == "GET":
            return httpx.Response(
                200,
                json=[
                    {"id": "z" * 24, "name": "Acme", "archived": False, "workspaceId": WORKSPACE}
                ],
            )
        return original(request)

    backend.responder = responder

    async def reject(context: Any, params: Any) -> ElicitResult:
        return ElicitResult(action="accept", content={"decision": "reject"})

    args = {
        "clockify_invoice_client_work": {
            "client": "Acme",
            "currency": "USD",
            "number": "INV-1",
            "issued_date": "2026-08-13",
            "due_date": "2026-09-13",
        },
        "clockify_request_time_off": {
            "policy": "Vacation",
            "start": "2026-09-01T00:00:00Z",
            "end": "2026-09-05T00:00:00Z",
        },
        "clockify_schedule_work": {
            "project": "Internal",
            "start": "2026-09-01T00:00:00Z",
            "end": "2026-09-05T00:00:00Z",
            "hours_per_day": 4,
        },
    }[tool]
    async with Client(make_server(backend), elicitation_callback=reject) as client:
        payload = payload_of(await client.call_tool(tool, args))
    assert payload["state"] == "rejected"
    assert backend.mutations == []
