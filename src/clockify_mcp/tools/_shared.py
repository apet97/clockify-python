# pyright: reportUnusedFunction=false
"""Shared helpers for raw read tools.


Every tool dispatches through `client.raw`, which sits on the same
`ReadOnlyExecutor` boundary as the resource methods: a mutating operation is
refused before any HTTP request regardless of what is registered here.
"""

from typing import Any

from mcp.types import ToolAnnotations

from clockify.client import ClockifyClient
from clockify.errors import ClockifyError
from clockify_mcp.errors import ToolError, to_tool_error
from clockify_mcp.result import ReadResult, read_result

READ_ANNOTATIONS = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=True,
)


async def raw_read(
    client: ClockifyClient,
    operation_id: str,
    *,
    path: dict[str, str] | None = None,
    query: dict[str, Any] | None = None,
    body: Any = None,
    warnings: list[str] | None = None,
) -> ReadResult:
    try:
        response = await client.raw.call(operation_id, path=path, query=query, body=body)
    except ClockifyError as exc:
        raise to_tool_error(exc) from exc
    return read_result(response, response.data, warnings=warnings)


def workspace_of(client: ClockifyClient, workspace_id: str | None) -> str:
    resolved = workspace_id or client.workspace_id
    if not resolved:
        raise ToolError(
            "workspace_id is required: pass it to the tool or set CLOCKIFY_WORKSPACE_ID"
        )
    return resolved
