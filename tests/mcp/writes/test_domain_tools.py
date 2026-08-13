# pyright: reportPrivateUsage=false, reportMissingParameterType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportAttributeAccessIssue=false
"""Wiring proof for every raw write tool.

One parametrized case per registered write tool: approving the preview
dispatches exactly the expected wire request once; rejecting dispatches
nothing. The case table is the reviewable surface — adding a write tool
without a row here fails `test_every_write_tool_has_a_case`.
"""

import json as jsonlib
from dataclasses import dataclass
from typing import Any

import httpx
import pytest
from mcp.types import CallToolResult, ElicitResult, TextContent

from clockify_mcp.context import ServerConfig
from clockify_mcp.full_server import build_full_server
from clockify_mcp.risk import RISK_BY_TOOL, Risk
from mcp import Client

from ..conftest import MockBackend, make_mock_client

WORKSPACE = "w-test"
TAG = "a" * 24
CONFIG = ServerConfig(api_key="test-key", addon_token=None, workspace_id=WORKSPACE)


@dataclass(frozen=True)
class Case:
    tool: str
    args: dict[str, Any]
    method: str
    path: str
    body: Any = None  # exact JSON body (dict or list), or None for empty
    query: dict[str, str] | None = None


USER = "b" * 24
ENTRY = "c" * 24

CASES = [
    Case(
        tool="clockify_tags_update",
        args={"tag_id": TAG, "name": "renamed"},
        method="PUT",
        path=f"/workspaces/{WORKSPACE}/tags/{TAG}",
        body={"name": "renamed"},
    ),
    Case(
        tool="clockify_tags_delete",
        args={"tag_id": TAG},
        method="DELETE",
        path=f"/workspaces/{WORKSPACE}/tags/{TAG}",
    ),
    Case(
        tool="clockify_time_entries_create",
        args={"body": {"start": "2026-08-13T08:00:00Z", "description": "work"}},
        method="POST",
        path=f"/workspaces/{WORKSPACE}/time-entries",
        body={"start": "2026-08-13T08:00:00Z", "description": "work"},
    ),
    Case(
        tool="clockify_time_entries_create_for_user",
        args={"user_id": USER, "body": {"start": "2026-08-13T08:00:00Z"}},
        method="POST",
        path=f"/workspaces/{WORKSPACE}/user/{USER}/time-entries",
        body={"start": "2026-08-13T08:00:00Z"},
    ),
    Case(
        tool="clockify_time_entries_update",
        args={"time_entry_id": ENTRY, "body": {"start": "2026-08-13T08:00:00Z"}},
        method="PUT",
        path=f"/workspaces/{WORKSPACE}/time-entries/{ENTRY}",
        body={"start": "2026-08-13T08:00:00Z"},
    ),
    Case(
        tool="clockify_time_entries_duplicate",
        args={"user_id": USER, "time_entry_id": ENTRY},
        method="POST",
        path=f"/workspaces/{WORKSPACE}/user/{USER}/time-entries/{ENTRY}/duplicate",
    ),
    Case(
        tool="clockify_time_entries_stop_timer",
        args={"user_id": USER, "end": "2026-08-13T09:00:00Z"},
        method="PATCH",
        path=f"/workspaces/{WORKSPACE}/user/{USER}/time-entries",
        body={"end": "2026-08-13T09:00:00Z"},
    ),
    Case(
        tool="clockify_time_entries_mark_invoiced",
        args={"time_entry_ids": [ENTRY], "invoiced": True},
        method="PATCH",
        path=f"/workspaces/{WORKSPACE}/time-entries/invoiced",
        body={"timeEntryIds": [ENTRY], "invoiced": True},
    ),
    Case(
        tool="clockify_time_entries_bulk_update_for_user",
        args={"user_id": USER, "entries": [{"start": "2026-08-13T08:00:00Z"}]},
        method="PUT",
        path=f"/workspaces/{WORKSPACE}/user/{USER}/time-entries",
        body=[{"start": "2026-08-13T08:00:00Z"}],
    ),
    Case(
        tool="clockify_time_entries_delete",
        args={"time_entry_id": ENTRY},
        method="DELETE",
        path=f"/workspaces/{WORKSPACE}/time-entries/{ENTRY}",
    ),
    Case(
        tool="clockify_time_entries_delete_all_for_user",
        args={"user_id": USER, "time_entry_ids": [ENTRY]},
        method="DELETE",
        path=f"/workspaces/{WORKSPACE}/user/{USER}/time-entries",
        query={"time-entry-ids": ENTRY},
    ),
]

# Tools proven by their own dedicated files, not by a generic case here.
DEDICATED = {
    "clockify_tags_create",  # tests/mcp/writes/test_wave1_tags_create.py
    # Write workflows: tests/mcp/test_workflows_write.py
    "clockify_start_work",
    "clockify_stop_work",
    "clockify_switch_work",
    "clockify_log_work",
    "clockify_fix_entry",
    "clockify_create_work_package",
    "clockify_demo_seed",
    "clockify_invoice_client_work",
    "clockify_record_expense",
    "clockify_request_time_off",
    "clockify_schedule_work",
    "clockify_setup_webhook",
    "clockify_demo_cleanup",
}


def minimal_instance(model: type[Any]) -> Any:
    """Build a model instance with only required fields, synthetically filled."""
    from pydantic import BaseModel
    from pydantic_core import PydanticUndefined

    assert issubclass(model, BaseModel)
    values: dict[str, Any] = {}
    for name, field in model.model_fields.items():
        if field.default is not PydanticUndefined or field.default_factory is not None:
            continue
        values[name] = _synthetic(name, field.annotation)
    return model.model_validate(values, by_name=True)


def _synthetic(name: str, annotation: Any) -> Any:
    import types
    import typing
    from enum import Enum

    from pydantic import BaseModel

    origin = typing.get_origin(annotation)
    if origin in (typing.Union, types.UnionType):
        non_none = [a for a in typing.get_args(annotation) if a is not type(None)]
        return _synthetic(name, non_none[0])
    if origin in (list, tuple, set):
        return []
    if origin is typing.Literal:
        return typing.get_args(annotation)[0]
    if isinstance(annotation, type):
        if issubclass(annotation, Enum):
            return next(iter(annotation)).value
        if issubclass(annotation, BaseModel):
            return minimal_instance(annotation)
        if annotation is bool:
            return True
        if annotation in (int, float):
            return 1
        if annotation is str:
            if "url" in name.lower():
                return "https://hooks.example.com/x"
            if "date" in name.lower() or name.lower() in ("start", "end", "since"):
                return "2026-08-13T08:00:00Z"
            return "x"
    return "x"


def generated_cases() -> list[Case]:
    """One case per generator-produced tool, derived from the registry."""
    import clockify.models as models_module
    from clockify.operations.registry import ALL_OPERATIONS
    from clockify_mcp.writes.tools import _DOMAIN_MODULES

    handwritten = {case.tool for case in CASES} | DEDICATED
    # tool name -> operation, following the generator's naming convention
    by_tool = {
        f"clockify_{op.resource}_{op.sdk_method}": op
        for op in ALL_OPERATIONS
        if op.semantics.mutates
    }
    # models per operation, recovered from the module sources' GuardedOp calls
    import inspect
    import re

    model_by_op: dict[str, str] = {}
    for module in _DOMAIN_MODULES:
        source = inspect.getsource(module)
        for match in re.finditer(r'operation_id="([^"]+)",\s*body_model=([A-Za-z_0-9]+)', source):
            model_by_op[match.group(1)] = match.group(2)

    cases: list[Case] = []
    for tool, risk in sorted(RISK_BY_TOOL.items()):
        if risk is Risk.READ or tool in handwritten:
            continue
        operation = by_tool[tool]
        args: dict[str, Any] = {}
        path = operation.path
        for param in operation.path_parameters:
            if param == "workspaceId":
                path = path.replace("{workspaceId}", WORKSPACE)
                continue
            typed_submit = operation.operation_id in (
                "createApprrovalRequest_1",
                "createApprovalForOtherWithType",
            ) and param in ("type", "approvalRequestId")
            arg = (
                "approval_type" if typed_submit else re.sub(r"(?<!^)(?=[A-Z])", "_", param).lower()
            )
            value = "1" if param == "order" else "a" * 24
            if typed_submit:
                value = "TIMESHEET"
            args[arg] = int(value) if param == "order" else value
            path = path.replace("{" + param + "}", str(value))
        query_expected: dict[str, str] | None = None
        for parameter in operation.query_parameters:
            if parameter.required:
                args[parameter.python_name] = True
                query_expected = {**(query_expected or {}), parameter.wire_name: "true"}
        body = None
        model_name = model_by_op.get(operation.operation_id)
        if model_name:
            instance = minimal_instance(getattr(models_module, model_name))
            args["body"] = instance.model_dump(by_alias=True, exclude_none=True)
            body = args["body"]
        cases.append(
            Case(
                tool=tool,
                args=args,
                method=operation.http_method,
                path=path,
                body=body,
            )
        )
    return cases


ALL_CASES = CASES + generated_cases()


class RecordingBackend(MockBackend):
    def __init__(self) -> None:
        super().__init__()
        self.mutations: list[httpx.Request] = []

        def responder(request: httpx.Request) -> httpx.Response:
            if request.method in ("POST", "PUT", "PATCH", "DELETE"):
                self.mutations.append(request)
                return httpx.Response(200, json={"id": TAG})
            return httpx.Response(200, json=[])

        self.responder = responder


def make_server(backend: RecordingBackend):  # type: ignore[no-untyped-def]
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
    return jsonlib.loads(first.text)


async def decide(client_decision: str, tool: str, args: dict[str, Any], backend: RecordingBackend):  # type: ignore[no-untyped-def]
    async def callback(context: Any, params: Any) -> ElicitResult:
        return ElicitResult(action="accept", content={"decision": client_decision})

    server = make_server(backend)
    async with Client(server, elicitation_callback=callback) as client:
        result = await client.call_tool(tool, args)
    return payload_of(result)


def test_every_write_tool_has_a_case() -> None:
    guarded_and_routine = {
        name for name, risk in RISK_BY_TOOL.items() if risk is not Risk.READ
    } - DEDICATED
    covered = {case.tool for case in ALL_CASES}
    assert covered == guarded_and_routine, (
        f"missing cases: {sorted(guarded_and_routine - covered)}; "
        f"stale cases: {sorted(covered - guarded_and_routine)}"
    )


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda case: case.tool)
async def test_approve_dispatches_the_exact_request(case: Case) -> None:
    backend = RecordingBackend()
    payload = await decide("approve", case.tool, case.args, backend)
    assert payload["state"] in ("succeeded", "reconciled"), payload
    assert len(backend.mutations) == 1
    request = backend.mutations[0]
    assert request.method == case.method
    assert request.url.path.endswith(case.path)
    from clockify.operations.model import RequestEncoding
    from clockify.operations.registry import BY_ID as _BY_ID

    operation = next(
        (op for op in _BY_ID.values() if f"clockify_{op.resource}_{op.sdk_method}" == case.tool),
        None,
    )
    if operation is not None and operation.request_encoding is RequestEncoding.MULTIPART:
        assert case.body is not None and request.content  # form-encoded fields
    elif case.body is not None:
        assert jsonlib.loads(request.content) == case.body
    else:
        assert request.content in (b"", b"null")
    for key, value in (case.query or {}).items():
        assert request.url.params[key] == value


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda case: case.tool)
async def test_reject_dispatches_nothing(case: Case) -> None:
    if RISK_BY_TOOL[case.tool] is Risk.ROUTINE_WRITE:
        pytest.skip("routine tools have no approval round trip")
    backend = RecordingBackend()
    payload = await decide("reject", case.tool, case.args, backend)
    assert payload["state"] == "rejected"
    assert backend.mutations == []
