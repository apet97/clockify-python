"""Shared MCP test fixtures: a mock-backed read-only server."""

import json as jsonlib
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from clockify._transport.auth import Credential
from clockify._transport.executor import HttpExecutor, ReadOnlyExecutor
from clockify.client import ClockifyClient
from clockify_mcp.context import ServerConfig
from clockify_mcp.server import build_read_only_server

TEST_CONFIG = ServerConfig(api_key="test-key", addon_token=None, workspace_id="w-test")


class MockBackend:
    """Programmable Clockify backend; records every request that gets through."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.responder: Callable[[httpx.Request], httpx.Response] = lambda request: httpx.Response(
            200, json=[]
        )

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.responder(request)

    def respond_json(self, payload: Any, status: int = 200) -> None:
        self.responder = lambda request: httpx.Response(status, json=payload)

    def respond_by_path(self, table: dict[str, Any]) -> None:
        def responder(request: httpx.Request) -> httpx.Response:
            # Longest fragment first so "/workspaces/w" never shadows deeper paths.
            for fragment in sorted(table, key=len, reverse=True):
                if fragment in request.url.path:
                    return httpx.Response(200, json=table[fragment])
            return httpx.Response(200, json=[])

        self.responder = responder


def make_mock_client(backend: MockBackend, workspace_id: str | None = "w-test") -> ClockifyClient:
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(backend.handler))
    executor = ReadOnlyExecutor(
        HttpExecutor(client=http_client, credential=Credential(api_key="test-key"))
    )
    return ClockifyClient(workspace_id=workspace_id, http_client=http_client, _executor=executor)


@pytest.fixture()
def backend() -> MockBackend:
    return MockBackend()


@pytest.fixture()
def server(backend: MockBackend):  # type: ignore[no-untyped-def]
    return build_read_only_server(TEST_CONFIG, client=make_mock_client(backend))


def result_json(call_result: Any) -> Any:
    """Extract the structured payload from a CallToolResult."""
    if call_result.structured_content is not None:
        return call_result.structured_content
    return jsonlib.loads(call_result.content[0].text)
