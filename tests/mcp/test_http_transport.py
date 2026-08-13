# pyright: reportMissingParameterType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
"""Streamable HTTP transport: initialize, list, read, and a gated write."""

import contextlib
import json
from typing import Any, cast

import httpx
import httpx2
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult, ElicitResult, TextContent

from clockify_mcp.context import ServerConfig
from clockify_mcp.full_server import build_full_server
from clockify_mcp.risk import RISK_BY_TOOL
from mcp import Client

from .conftest import MockBackend, make_mock_client

CONFIG = ServerConfig(api_key="test-key", addon_token=None, workspace_id="w-test")
TAG_JSON = {"id": "t-http", "name": "http", "workspaceId": "w-test", "archived": False}


class WriteBackend(MockBackend):
    def __init__(self) -> None:
        super().__init__()
        self.mutations: list[httpx.Request] = []

        def responder(request: httpx.Request) -> httpx.Response:
            if request.method == "POST" and request.url.path.endswith("/tags"):
                self.mutations.append(request)
                return httpx.Response(201, json=TAG_JSON)
            if request.url.path.endswith("/tags/t-http"):
                return httpx.Response(200, json=TAG_JSON)
            return httpx.Response(200, json=[])

        self.responder = responder


@contextlib.asynccontextmanager
async def http_client_for(backend: WriteBackend):  # type: ignore[no-untyped-def]
    server = build_full_server(
        CONFIG,
        read_client=make_mock_client(backend),
        write_http_client=httpx.AsyncClient(transport=httpx.MockTransport(backend.handler)),
    )
    app = server.streamable_http_app(stateless_http=False)
    async with app.router.lifespan_context(app):
        http = httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app), base_url="http://127.0.0.1:8000"
        )
        async with http:
            yield streamable_http_client("http://127.0.0.1:8000/mcp", http_client=http)


def result_json(result: CallToolResult) -> dict[str, Any]:
    if isinstance(result.structured_content, dict):
        return cast(dict[str, Any], result.structured_content)
    first = result.content[0]
    assert isinstance(first, TextContent)
    return cast(dict[str, Any], json.loads(first.text))


async def approve(context: Any, params: Any) -> ElicitResult:
    return ElicitResult(action="accept", content={"decision": "approve"})


async def test_http_serves_full_surface_and_reads() -> None:
    backend = WriteBackend()
    async with http_client_for(backend) as transport, Client(transport, cache=None) as client:
        tools = await client.list_tools()
        assert {tool.name for tool in tools.tools} == set(RISK_BY_TOOL)
        result = await client.call_tool("clockify_tags_list", {})
        assert not result.is_error


async def test_http_gated_write_approves_end_to_end() -> None:
    backend = WriteBackend()
    async with (
        http_client_for(backend) as transport,
        Client(transport, elicitation_callback=approve, cache=None) as client,
    ):
        result = await client.call_tool("clockify_tags_create", {"name": "http"})
    payload = result_json(result)
    assert payload["state"] == "reconciled"
    assert len(backend.mutations) == 1
