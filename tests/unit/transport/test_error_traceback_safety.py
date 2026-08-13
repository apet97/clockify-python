"""Error objects and tracebacks must not retain upstream credentials."""

from collections.abc import Iterator

import httpx
import pytest

from clockify._transport.auth import Credential
from clockify._transport.executor import HttpExecutor
from clockify.errors import (
    ClockifyAPIError,
    ClockifyResponseValidationError,
    ClockifyTransportError,
)
from clockify.operations.model import Operation, Service
from clockify.operations.registry import BY_ID

_SYNTHETIC_SECRET = "traceback-secret-that-must-not-escape"
_READ_OPERATION = Operation(
    operation_id="testErrorTracebackRead",
    resource="tests",
    sdk_method="error_traceback_read",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/traceback-test",
    path_parameters=("workspaceId",),
)


@pytest.fixture(autouse=True)
def register_operation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(BY_ID, _READ_OPERATION.operation_id, _READ_OPERATION)


def _executor(handler: httpx.MockTransport) -> HttpExecutor:
    return HttpExecutor(
        client=httpx.AsyncClient(transport=handler),
        credential=Credential(api_key=_SYNTHETIC_SECRET),
    )


def _exception_debug_views(error: BaseException) -> Iterator[str]:
    """Yield public exception data and reprs of all retained traceback locals."""
    pending = [error]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        yield str(current)
        yield repr(current)
        traceback = current.__traceback__
        while traceback is not None:
            for name, value in traceback.tb_frame.f_locals.items():
                yield f"{name}={value!r}"
            traceback = traceback.tb_next
        if current.__cause__ is not None:
            pending.append(current.__cause__)
        if current.__context__ is not None:
            pending.append(current.__context__)


def _assert_exception_is_sanitized(error: BaseException) -> None:
    assert error.__cause__ is None
    assert error.__context__ is None
    assert all(_SYNTHETIC_SECRET not in view for view in _exception_debug_views(error))


async def test_api_error_traceback_does_not_retain_raw_body_or_secret() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={"message": _SYNTHETIC_SECRET, "nested": [_SYNTHETIC_SECRET]},
            headers={
                "Authorization": f"Bearer {_SYNTHETIC_SECRET}",
                "Cookie": f"session={_SYNTHETIC_SECRET}",
                "Proxy-Authorization": f"Basic {_SYNTHETIC_SECRET}",
                "Set-Cookie": f"session={_SYNTHETIC_SECRET}; Secure",
                "X-Addon-Token": _SYNTHETIC_SECRET,
                "X-Api-Key": _SYNTHETIC_SECRET,
                "X-Debug": f"safe prefix {_SYNTHETIC_SECRET}",
            },
        )

    with pytest.raises(ClockifyAPIError) as info:
        await _executor(httpx.MockTransport(handler)).execute(
            _READ_OPERATION, path_args={"workspaceId": "w"}
        )

    error = info.value
    _assert_exception_is_sanitized(error)
    assert error.headers is not None
    for name in (
        "Authorization",
        "Cookie",
        "Proxy-Authorization",
        "Set-Cookie",
        "X-Addon-Token",
        "X-Api-Key",
    ):
        assert error.headers[name] == "<redacted>"
    assert error.headers["X-Debug"] == "safe prefix <redacted>"


async def test_transport_error_has_no_raw_cause_or_traceback_local() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadError(f"failed with {_SYNTHETIC_SECRET}")

    with pytest.raises(ClockifyTransportError) as info:
        await _executor(httpx.MockTransport(handler)).execute(
            _READ_OPERATION, path_args={"workspaceId": "w"}
        )

    _assert_exception_is_sanitized(info.value)


async def test_invalid_json_error_has_no_parser_cause_or_raw_traceback_local() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=f'{{"message":"{_SYNTHETIC_SECRET}'.encode(),
            headers={"Content-Type": "application/json"},
        )

    with pytest.raises(ClockifyResponseValidationError) as info:
        await _executor(httpx.MockTransport(handler)).execute(
            _READ_OPERATION, path_args={"workspaceId": "w"}
        )

    _assert_exception_is_sanitized(info.value)
