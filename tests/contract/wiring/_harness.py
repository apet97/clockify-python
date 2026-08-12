"""Shared harness for the 168-case public-method wiring suite."""

import json as jsonlib
from typing import Any

import httpx

from clockify.client import ClockifyClient
from clockify.operations.registry import BY_PUBLIC_METHOD


class Capture:
    """Records the single request a wiring case dispatches."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []

    @property
    def request(self) -> httpx.Request:
        assert len(self.requests) == 1, f"expected exactly one request, saw {len(self.requests)}"
        return self.requests[0]

    def sent_json(self) -> Any:
        return jsonlib.loads(self.request.content)


def make_client(
    *,
    status: int = 200,
    json: Any = None,
    content: bytes | None = None,
    content_type: str | None = None,
    workspace_id: str | None = "w-default",
) -> tuple[ClockifyClient, Capture]:
    capture = Capture()

    def handler(request: httpx.Request) -> httpx.Response:
        capture.requests.append(request)
        headers = {"Content-Type": content_type} if content_type else None
        if content is not None:
            return httpx.Response(status, content=content, headers=headers)
        return httpx.Response(status, json=json, headers=headers)

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = ClockifyClient(
        api_key="wiring-test-key", workspace_id=workspace_id, http_client=http_client
    )
    return client, capture


def assert_wired(
    capture: Capture,
    *,
    resource: str,
    method: str,
    url: str,
    query: dict[str, list[str]] | None = None,
) -> None:
    """Assert the dispatched request matches the registry record for (resource, method)."""
    operation = BY_PUBLIC_METHOD[(resource, method)]
    request = capture.request
    assert request.method == operation.http_method
    assert str(request.url.copy_with(query=None)) == url
    if query is not None:
        for wire_name, expected in query.items():
            assert request.url.params.get_list(wire_name) == expected, wire_name
    else:
        assert not request.url.query
