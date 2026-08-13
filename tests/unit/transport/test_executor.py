"""HTTP executor contract tests over httpx.MockTransport."""

import asyncio
import json
from collections.abc import Callable, Coroutine
from dataclasses import replace
from typing import Any

import httpx
import pytest

from clockify._transport.auth import Credential
from clockify._transport.executor import HttpExecutor, ReadOnlyExecutor
from clockify.config import ReadRetryPolicy
from clockify.errors import (
    ClockifyAPIError,
    ClockifyAuthenticationError,
    ClockifyConfigurationError,
    ClockifyNotFoundError,
    ClockifyRateLimitError,
    ClockifyReadOnlyViolation,
    ClockifyTransportError,
    MutationOutcomeUnknownError,
)
from clockify.files import Upload
from clockify.operations.model import (
    MutationEffect,
    Operation,
    OperationSemantics,
    QueryParameter,
    ReplacementSemantics,
    RequestEncoding,
    ResponseKind,
    Service,
)
from clockify.operations.registry import BY_ID
from clockify.operations.time_entries import TIME_ENTRIES_DELETE_ALL_FOR_USER
from clockify.response import BinaryResponse, TextResponse
from clockify_mcp.errors import to_tool_error

READ_SEMANTICS = OperationSemantics(
    mutates=False, effect=MutationEffect.NONE, replacement=ReplacementSemantics.NOT_APPLICABLE
)
WRITE_SEMANTICS = OperationSemantics(
    mutates=True, effect=MutationEffect.CREATE, replacement=ReplacementSemantics.NOT_APPLICABLE
)

GET_READ = Operation(
    operation_id="testRead",
    resource="tests",
    sdk_method="read",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/things",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("name", "name"),
        QueryParameter("tags", "tags"),
        QueryParameter("joined", "joined", explode=False),
        QueryParameter("page_size", "page-size"),
        QueryParameter("archived", "archived"),
    ),
)

POST_READ = Operation(
    operation_id="testPostRead",
    resource="tests",
    sdk_method="search",
    http_method="POST",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/reports/summary",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
)

JSON_WRITE = Operation(
    operation_id="testWrite",
    resource="tests",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/things",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    semantics=WRITE_SEMANTICS,
)

# A mutating operation that uses GET would be a classic verb-heuristic trap:
# retry must consult semantics, never the verb.
GET_WRITE_TRAP = Operation(
    operation_id="testGetTrap",
    resource="tests",
    sdk_method="trap",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/trap",
    path_parameters=("workspaceId",),
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.TRANSITION,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

MULTIPART_WRITE = Operation(
    operation_id="testUpload",
    resource="tests",
    sdk_method="upload",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/files",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.MULTIPART,
    semantics=WRITE_SEMANTICS,
)


@pytest.fixture(autouse=True)
def register_test_operations(monkeypatch: pytest.MonkeyPatch) -> None:
    for operation in (GET_READ, POST_READ, JSON_WRITE, GET_WRITE_TRAP, MULTIPART_WRITE):
        monkeypatch.setitem(BY_ID, operation.operation_id, operation)


async def noop_request_hook(request: httpx.Request) -> None:
    return None


def make_executor(
    handler: "Callable[[httpx.Request], httpx.Response] | Callable[[httpx.Request], Coroutine[Any, Any, httpx.Response]]",
    *,
    retry_policy: ReadRetryPolicy | None = None,
    addon_token: str | None = None,
    service_urls: dict[Service, str] | None = None,
    allow_custom_hosts: bool = False,
) -> HttpExecutor:
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    credential = (
        Credential(addon_token=addon_token) if addon_token else Credential(api_key="test-key")
    )
    return HttpExecutor(
        client=client,
        credential=credential,
        retry_policy=retry_policy,
        service_urls=service_urls,
        allow_custom_hosts=allow_custom_hosts,
    )


class TestRouting:
    async def test_regular_service_url_and_path(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        await executor.execute(GET_READ, path_args={"workspaceId": "w1"})
        assert str(seen[0].url) == "https://api.clockify.me/api/v1/workspaces/w1/things"

    async def test_reports_service_url(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={})

        executor = make_executor(handler)
        await executor.execute(POST_READ, path_args={"workspaceId": "w1"}, body={"x": 1})
        assert seen[0].url.host == "reports.api.clockify.me"

    async def test_path_values_are_percent_encoded(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        await executor.execute(GET_READ, path_args={"workspaceId": "a/b c"})
        assert "/workspaces/a%2Fb%20c/things" in str(seen[0].url)

    async def test_effective_url_and_query_match_the_compiled_request(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        compiled = executor.compile(
            GET_READ,
            path_args={"workspaceId": "w"},
            query={"tags": ["a", "b"], "page_size": 25},
        )
        await executor._dispatch_compiled(  # pyright: ignore[reportPrivateUsage]
            GET_READ, compiled
        )
        expected_url = httpx.URL(compiled.url).copy_merge_params(compiled.params)
        assert seen[0].url == expected_url

    async def test_missing_path_arg_fails_before_network(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise AssertionError("must not reach network")

        executor = make_executor(handler)
        with pytest.raises(ClockifyConfigurationError, match="missing path parameters"):
            await executor.execute(GET_READ, path_args={})

    async def test_custom_host_requires_opt_in(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise AssertionError("must not reach network")

        executor = make_executor(
            handler, service_urls={Service.REGULAR: "https://evil.example.com/api/v1"}
        )
        with pytest.raises(ClockifyConfigurationError, match="allow_custom_hosts"):
            await executor.execute(GET_READ, path_args={"workspaceId": "w"})

    async def test_custom_host_allowed_with_opt_in(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(
            handler,
            service_urls={Service.REGULAR: "https://self-hosted.example.com/api/v1"},
            allow_custom_hosts=True,
        )
        await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert seen[0].url.host == "self-hosted.example.com"


class TestAuth:
    async def test_api_key_header(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert seen[0].headers["X-Api-Key"] == "test-key"
        assert "X-Addon-Token" not in seen[0].headers

    async def test_addon_token_header(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler, addon_token="addon-secret")
        await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert seen[0].headers["X-Addon-Token"] == "addon-secret"
        assert "X-Api-Key" not in seen[0].headers

    def test_both_credentials_rejected(self) -> None:
        with pytest.raises(ClockifyConfigurationError):
            Credential(api_key="a", addon_token="b")

    def test_neither_credential_rejected(self) -> None:
        with pytest.raises(ClockifyConfigurationError):
            Credential()

    def test_credential_repr_redacts_secret(self) -> None:
        credential = Credential(api_key="super-secret")
        assert "super-secret" not in repr(credential)


class TestHeaders:
    async def test_defaults_present(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert seen[0].headers["User-Agent"].startswith("clockify-python-115/")
        assert seen[0].headers["X-Request-Id"]

    async def test_caller_headers_win(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        await executor.execute(
            GET_READ,
            path_args={"workspaceId": "w"},
            headers={"User-Agent": "custom-agent", "X-Request-Id": "rid-1"},
        )
        assert seen[0].headers["User-Agent"] == "custom-agent"
        assert seen[0].headers["X-Request-Id"] == "rid-1"

    @pytest.mark.parametrize(
        "header_name",
        [
            "Host",
            "host",
            "hOsT",
            ":authority",
            ":AUTHORITY",
            "X-Api-Key",
            "x-api-key",
            "X-aPi-KeY",
            "X-Addon-Token",
            "x-addon-token",
            "X-aDdOn-ToKeN",
        ],
    )
    async def test_protected_caller_header_rejected_before_network(self, header_name: str) -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        with pytest.raises(ClockifyConfigurationError, match="protected header"):
            await executor.execute(
                GET_READ,
                path_args={"workspaceId": "w"},
                headers={header_name: "caller-controlled"},
            )
        assert calls == 0

    @pytest.mark.parametrize("addon_token", [None, "configured-addon-token"])
    async def test_exactly_one_configured_credential_reaches_transport(
        self, addon_token: str | None
    ) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler, addon_token=addon_token)
        await executor.execute(
            GET_READ,
            path_args={"workspaceId": "w"},
            headers={"Authorization": "caller-scheme caller-value", "X-Trace": "trace-1"},
        )
        credential_headers = [
            name for name in ("X-Api-Key", "X-Addon-Token") if name in seen[0].headers
        ]
        assert credential_headers == ["X-Addon-Token" if addon_token else "X-Api-Key"]
        assert seen[0].headers["Authorization"] == "caller-scheme caller-value"
        assert seen[0].headers["X-Trace"] == "trace-1"

    @pytest.mark.parametrize(
        "headers",
        [
            {"Host": "alternate.example.com"},
            {"X-Api-Key": "client-default-key"},
            {"X-Addon-Token": "client-default-token"},
        ],
    )
    async def test_protected_client_default_header_is_rejected_before_network(
        self, headers: dict[str, str]
    ) -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(200, json=[])

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler), headers=headers)
        executor = HttpExecutor(client=client, credential=Credential(api_key="configured-key"))
        with pytest.raises(ClockifyConfigurationError, match="protected header"):
            await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert calls == 0

    @pytest.mark.parametrize(
        "client_options",
        [
            {"params": {"injected": "true"}},
            {"auth": ("user", "password")},
            {"event_hooks": {"request": [noop_request_hook]}},
        ],
    )
    async def test_unsafe_client_default_is_rejected_before_network(
        self, client_options: dict[str, Any]
    ) -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(200, json=[])

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler), **client_options)
        executor = HttpExecutor(client=client, credential=Credential(api_key="configured-key"))
        with pytest.raises(ClockifyConfigurationError, match="injected HTTP client"):
            await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert calls == 0


class TestQuerySerialization:
    async def test_exact_wire_names_and_styles(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        await executor.execute(
            GET_READ,
            path_args={"workspaceId": "w"},
            query={
                "name": "x y",
                "tags": ["a", "b"],
                "joined": ["c", "d"],
                "page_size": 25,
                "archived": False,
            },
        )
        url = seen[0].url
        assert url.params.get_list("tags") == ["a", "b"]  # explode=True repeats the key
        assert url.params["joined"] == "c,d"  # explode=False comma-joins
        assert url.params["page-size"] == "25"  # python name page_size -> wire page-size
        assert url.params["archived"] == "false"  # bool lowered
        assert url.params["name"] == "x y"

    async def test_none_values_omitted(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        await executor.execute(
            GET_READ, path_args={"workspaceId": "w"}, query={"name": None, "archived": None}
        )
        assert not seen[0].url.query

    async def test_unknown_query_rejected_before_network(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise AssertionError("must not reach network")

        executor = make_executor(handler)
        with pytest.raises(ClockifyConfigurationError, match="unknown query parameters"):
            await executor.execute(GET_READ, path_args={"workspaceId": "w"}, query={"nope": 1})

    async def test_empty_required_collection_blocks_destructive_request(self) -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        with pytest.raises(ClockifyConfigurationError, match="must not be empty"):
            await executor.execute(
                TIME_ENTRIES_DELETE_ALL_FOR_USER,
                path_args={"workspaceId": "w", "userId": "u"},
                query={"time_entry_ids": []},
            )
        assert calls == 0


class TestBodies:
    async def test_json_body_none_vs_omitted(self) -> None:
        from pydantic import BaseModel, ConfigDict, Field

        class Body(BaseModel):
            model_config = ConfigDict(populate_by_name=True)
            keep_null: str | None = Field(default=None, alias="keepNull")
            drop_unset: str | None = Field(default=None, alias="dropUnset")

        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={})

        executor = make_executor(handler)
        await executor.execute(
            JSON_WRITE, path_args={"workspaceId": "w"}, body=Body.model_validate({"keepNull": None})
        )
        sent = json.loads(seen[0].content)
        assert sent == {"keepNull": None}  # explicit None kept, unset dropped

    async def test_multipart_files_and_fields(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={})

        executor = make_executor(handler)
        await executor.execute(
            MULTIPART_WRITE,
            path_args={"workspaceId": "w"},
            body={"amount": 12},
            files={"file": Upload(filename="r.png", content=b"\x89PNG", content_type="image/png")},
        )
        content_type = seen[0].headers["Content-Type"]
        assert content_type.startswith("multipart/form-data")
        assert b"r.png" in seen[0].content
        assert b"\x89PNG" in seen[0].content
        assert b'name="amount"' in seen[0].content

    async def test_body_on_bodyless_operation_rejected(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise AssertionError("must not reach network")

        executor = make_executor(handler)
        with pytest.raises(ClockifyConfigurationError, match="no request body"):
            await executor.execute(GET_READ, path_args={"workspaceId": "w"}, body={"x": 1})


class TestResponses:
    async def test_json_decoded(self) -> None:
        executor = make_executor(lambda request: httpx.Response(200, json={"id": "1"}))
        result = await executor.execute(POST_READ, path_args={"workspaceId": "w"}, body={})
        assert result.data == {"id": "1"}
        assert result.status_code == 200

    async def test_empty_json_body_becomes_none(self) -> None:
        executor = make_executor(lambda request: httpx.Response(200))
        result = await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert result.data is None

    async def test_bytes_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        op = Operation(
            operation_id="testBytes",
            resource="tests",
            sdk_method="download",
            http_method="GET",
            service=Service.REGULAR,
            path="/workspaces/{workspaceId}/file",
            path_parameters=("workspaceId",),
            response_kind=ResponseKind.BYTES,
        )
        monkeypatch.setitem(BY_ID, op.operation_id, op)
        executor = make_executor(
            lambda request: httpx.Response(
                200,
                content=b"\x00\xffbinary",
                headers={
                    "Content-Type": "application/pdf",
                    "Content-Disposition": 'attachment; filename="receipt.pdf"',
                },
            )
        )
        result = await executor.execute(op, path_args={"workspaceId": "w"})
        assert isinstance(result.data, BinaryResponse)
        assert result.data.content == b"\x00\xffbinary"
        assert result.data.filename == "receipt.pdf"

    async def test_text_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        op = Operation(
            operation_id="testText",
            resource="tests",
            sdk_method="csv",
            http_method="GET",
            service=Service.REGULAR,
            path="/workspaces/{workspaceId}/csv",
            path_parameters=("workspaceId",),
            response_kind=ResponseKind.TEXT,
        )
        monkeypatch.setitem(BY_ID, op.operation_id, op)
        executor = make_executor(
            lambda request: httpx.Response(
                200, content=b"a,b\n1,2", headers={"Content-Type": "text/csv"}
            )
        )
        result = await executor.execute(op, path_args={"workspaceId": "w"})
        assert isinstance(result.data, TextResponse)
        assert result.data.text == "a,b\n1,2"

    async def test_none_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        op = Operation(
            operation_id="testNone",
            resource="tests",
            sdk_method="remove",
            http_method="DELETE",
            service=Service.REGULAR,
            path="/workspaces/{workspaceId}/thing",
            path_parameters=("workspaceId",),
            response_kind=ResponseKind.NONE,
            semantics=OperationSemantics(
                mutates=True,
                effect=MutationEffect.DELETE,
                replacement=ReplacementSemantics.NOT_APPLICABLE,
            ),
        )
        monkeypatch.setitem(BY_ID, op.operation_id, op)
        executor = make_executor(lambda request: httpx.Response(204))
        result = await executor.execute(op, path_args={"workspaceId": "w"})
        assert result.data is None

    @pytest.mark.parametrize(
        ("content_type", "content", "expected_type"),
        [
            ("application/json", b'{"a": 1}', dict),
            ("text/csv", b"a,b", TextResponse),
            ("application/pdf", b"\x00\x01", BinaryResponse),
            ("application/vnd.unknown", b"\x00\x01", BinaryResponse),
        ],
    )
    async def test_content_negotiated(
        self,
        content_type: str,
        content: bytes,
        expected_type: type,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        op = Operation(
            operation_id="testNegotiated",
            resource="tests",
            sdk_method="view",
            http_method="GET",
            service=Service.REPORTS,
            path="/shared/{id}",
            path_parameters=("id",),
            response_kind=ResponseKind.CONTENT_NEGOTIATED,
        )
        monkeypatch.setitem(BY_ID, op.operation_id, op)
        executor = make_executor(
            lambda request: httpx.Response(
                200, content=content, headers={"Content-Type": content_type}
            )
        )
        result = await executor.execute(op, path_args={"id": "s1"})
        assert isinstance(result.data, expected_type)


class TestErrors:
    @pytest.mark.parametrize(
        ("status", "error_type"),
        [
            (401, ClockifyAuthenticationError),
            (404, ClockifyNotFoundError),
            (429, ClockifyRateLimitError),
            (400, ClockifyAPIError),
        ],
    )
    async def test_status_mapping(self, status: int, error_type: type) -> None:
        executor = make_executor(
            lambda request: httpx.Response(
                status, json={"message": "nope", "code": 4030}, headers={"Retry-After": "2"}
            )
        )
        with pytest.raises(error_type) as info:
            await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        error = info.value
        assert error.status_code == status
        assert error.api_code == 4030
        assert error.operation_id == "testRead"
        if status == 429:
            assert error.retry_after == 2.0

    async def test_redirect_is_an_error_not_followed(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(302, headers={"Location": "https://elsewhere.example.com/x"})

        executor = make_executor(handler)
        with pytest.raises(ClockifyAPIError) as info:
            await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert info.value.status_code == 302
        assert len(seen) == 1  # no second request to another host

    @pytest.mark.parametrize("addon_token", [None, "reflected-addon-token"])
    @pytest.mark.parametrize("response_kind", ["json", "text"])
    async def test_reflected_configured_secret_is_absent_from_public_errors(
        self, addon_token: str | None, response_kind: str
    ) -> None:
        secret = addon_token or "test-key"

        def handler(request: httpx.Request) -> httpx.Response:
            if response_kind == "json":
                return httpx.Response(
                    400,
                    json={
                        "message": f"safe prefix {secret} safe suffix",
                        "nested": {"X-Api-Key": secret},
                        secret: "configured secret used as a key",
                        "refreshToken": secret,
                        "items": ["safe", {"token": secret}],
                        "code": "SAFE_CODE",
                    },
                    headers={"X-Debug": f"Authorization: Bearer {secret}"},
                )
            return httpx.Response(400, text=f"safe prefix {secret} safe suffix")

        executor = make_executor(handler, addon_token=addon_token)
        with pytest.raises(ClockifyAPIError) as info:
            await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        error = info.value
        public_views = (
            str(error),
            repr(error),
            repr(error.body),
            repr(error.headers),
            str(to_tool_error(error)),
        )
        assert all(secret not in view for view in public_views)
        assert "safe prefix" in str(error)
        if response_kind == "json":
            assert error.api_code == "SAFE_CODE"
            assert error.body["<redacted-key-1>"] == "<redacted>"
            assert error.body["<redacted-key-2>"] == "<redacted>"

    async def test_large_json_error_is_bounded_and_keeps_safe_diagnostics(self) -> None:
        executor = make_executor(
            lambda request: httpx.Response(
                429,
                json={"message": "x" * (1024 * 1024), "code": "RATE_LIMITED"},
                headers={"Retry-After": "2", "X-Request-Id": "upstream-rid"},
            )
        )
        with pytest.raises(ClockifyRateLimitError) as info:
            await executor.execute(
                GET_READ,
                path_args={"workspaceId": "w"},
                headers={"X-Request-Id": "caller-rid"},
            )
        error = info.value
        assert len(str(error)) <= 500
        assert len(repr(error.body)) <= 5000
        assert error.operation_id == "testRead"
        assert error.status_code == 429
        assert error.request_id == "caller-rid"
        assert error.api_code == "RATE_LIMITED"
        assert error.retry_after == 2.0


class TestRetryBoundary:
    @pytest.mark.parametrize(
        ("retry_after", "expected"),
        [
            ("2", 2.0),
            ("2.5", 2.5),
            ("-1", None),
            ("not-a-date", None),
            (None, None),
            ("Wed, 12 Aug 2026 08:30:05 GMT", 5.0),
            ("Wed, 12 Aug 2026 08:29:55 GMT", 0.0),
        ],
    )
    async def test_retry_after_controls_actual_retry_delay(
        self, retry_after: str | None, expected: float | None
    ) -> None:
        calls = 0
        delays: list[float | None] = []

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            if calls == 1:
                headers = {"Date": "Wed, 12 Aug 2026 08:30:00 GMT"}
                if retry_after is not None:
                    headers["Retry-After"] = retry_after
                return httpx.Response(503, headers=headers)
            return httpx.Response(200, json=[])

        executor = make_executor(handler, retry_policy=ReadRetryPolicy(max_attempts=2))

        async def capture_sleep(attempt: int, retry_delay: float | None) -> None:
            delays.append(retry_delay)

        executor._sleep = capture_sleep  # type: ignore[method-assign]
        await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert delays == [expected]

    async def test_read_retries_on_retryable_status(self) -> None:
        calls = {"n": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            if calls["n"] < 3:
                return httpx.Response(503)
            return httpx.Response(200, json=[])

        executor = make_executor(
            handler, retry_policy=ReadRetryPolicy(max_attempts=3, base_delay=0.001)
        )
        result = await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert result.data == []
        assert calls["n"] == 3

    async def test_post_read_is_retryable(self) -> None:
        calls = {"n": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            if calls["n"] == 1:
                return httpx.Response(500)
            return httpx.Response(200, json={})

        executor = make_executor(
            handler, retry_policy=ReadRetryPolicy(max_attempts=2, base_delay=0.001)
        )
        await executor.execute(POST_READ, path_args={"workspaceId": "w"}, body={})
        assert calls["n"] == 2

    async def test_write_never_retried_even_with_policy(self) -> None:
        calls = {"n": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            return httpx.Response(503)

        executor = make_executor(
            handler, retry_policy=ReadRetryPolicy(max_attempts=3, base_delay=0.001)
        )
        with pytest.raises(ClockifyAPIError):
            await executor.execute(JSON_WRITE, path_args={"workspaceId": "w"}, body={})
        assert calls["n"] == 1

    async def test_get_verb_mutation_trap_not_retried(self) -> None:
        """Retry consults semantics, not the HTTP verb."""
        calls = {"n": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            return httpx.Response(503)

        executor = make_executor(
            handler, retry_policy=ReadRetryPolicy(max_attempts=3, base_delay=0.001)
        )
        with pytest.raises(ClockifyAPIError):
            await executor.execute(GET_WRITE_TRAP, path_args={"workspaceId": "w"})
        assert calls["n"] == 1

    async def test_no_retry_without_policy(self) -> None:
        calls = {"n": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            return httpx.Response(503)

        executor = make_executor(handler)
        with pytest.raises(ClockifyAPIError):
            await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert calls["n"] == 1


class TestTransportFailures:
    async def test_read_connect_error_is_plain_transport_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("refused")

        executor = make_executor(handler)
        with pytest.raises(ClockifyTransportError) as info:
            await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert not isinstance(info.value, MutationOutcomeUnknownError)

    async def test_write_connect_error_is_plain_transport_error(self) -> None:
        """A connect failure provably never reached Clockify."""

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("refused")

        executor = make_executor(handler)
        with pytest.raises(ClockifyTransportError) as info:
            await executor.execute(JSON_WRITE, path_args={"workspaceId": "w"}, body={})
        assert not isinstance(info.value, MutationOutcomeUnknownError)

    async def test_write_mid_flight_failure_is_outcome_unknown(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("timed out mid-exchange")

        executor = make_executor(handler)
        with pytest.raises(MutationOutcomeUnknownError):
            await executor.execute(JSON_WRITE, path_args={"workspaceId": "w"}, body={})

    async def test_read_transport_error_is_redacted_and_bounded(self) -> None:
        secret = "configured-secret"

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadError(f"{secret} " + "x" * 5000)

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        executor = HttpExecutor(client=client, credential=Credential(api_key=secret))
        with pytest.raises(ClockifyTransportError) as info:
            await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert secret not in str(info.value)
        assert len(str(info.value)) <= 500

    async def test_cancellation_propagates(self) -> None:
        started = asyncio.Event()

        async def handler(request: httpx.Request) -> httpx.Response:
            started.set()
            await asyncio.sleep(30)
            return httpx.Response(200, json=[])

        executor = make_executor(handler)
        task = asyncio.create_task(executor.execute(GET_READ, path_args={"workspaceId": "w"}))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_in_flight_write_cancellation_is_outcome_unknown(self) -> None:
        started = asyncio.Event()

        async def handler(request: httpx.Request) -> httpx.Response:
            started.set()
            await asyncio.sleep(30)
            return httpx.Response(200, json={})

        executor = make_executor(handler)
        task = asyncio.create_task(
            executor.execute(JSON_WRITE, path_args={"workspaceId": "w"}, body={})
        )
        await started.wait()
        task.cancel()
        with pytest.raises(MutationOutcomeUnknownError):
            await task


class TestTimeouts:
    async def test_client_default_timeout_is_preserved(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        client = httpx.AsyncClient(
            transport=httpx.MockTransport(handler), timeout=httpx.Timeout(123.0)
        )
        executor = HttpExecutor(client=client, credential=Credential(api_key="test-key"))
        await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert seen[0].extensions["timeout"] == {
            "connect": 123.0,
            "read": 123.0,
            "write": 123.0,
            "pool": 123.0,
        }

    async def test_per_call_timeout_overrides_client_default(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=[])

        client = httpx.AsyncClient(
            transport=httpx.MockTransport(handler), timeout=httpx.Timeout(123.0)
        )
        executor = HttpExecutor(client=client, credential=Credential(api_key="test-key"))
        await executor.execute(
            GET_READ,
            path_args={"workspaceId": "w"},
            timeout=httpx.Timeout(7.0),
        )
        assert seen[0].extensions["timeout"] == {
            "connect": 7.0,
            "read": 7.0,
            "write": 7.0,
            "pool": 7.0,
        }


class TestReadOnlyExecutor:
    async def test_read_passes_through(self) -> None:
        executor = ReadOnlyExecutor(make_executor(lambda request: httpx.Response(200, json=[])))
        result = await executor.execute(GET_READ, path_args={"workspaceId": "w"})
        assert result.data == []

    async def test_mutation_blocked_before_network(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise AssertionError("mutation must never reach the transport")

        executor = ReadOnlyExecutor(make_executor(handler))
        with pytest.raises(ClockifyReadOnlyViolation):
            await executor.execute(JSON_WRITE, path_args={"workspaceId": "w"}, body={})

    async def test_get_verb_mutation_blocked(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise AssertionError("mutation must never reach the transport")

        executor = ReadOnlyExecutor(make_executor(handler))
        with pytest.raises(ClockifyReadOnlyViolation):
            await executor.execute(GET_WRITE_TRAP, path_args={"workspaceId": "w"})

    async def test_forged_registered_operation_is_rejected(self) -> None:
        forged_write = replace(JSON_WRITE, semantics=READ_SEMANTICS)

        def handler(request: httpx.Request) -> httpx.Response:
            raise AssertionError("forged operation must not reach the transport")

        executor = ReadOnlyExecutor(make_executor(handler))
        with pytest.raises(ClockifyConfigurationError, match="operation registry"):
            await executor.execute(
                forged_write,
                path_args={"workspaceId": "w"},
                body={},
            )

    async def test_compiled_write_cannot_be_dispatched_as_a_read(self) -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(200, json=[])

        inner = make_executor(handler, retry_policy=ReadRetryPolicy(max_attempts=2))
        compiled_write = inner.compile(
            JSON_WRITE,
            path_args={"workspaceId": "w"},
            body={},
        )
        with pytest.raises(ClockifyConfigurationError, match="compiled request operation"):
            await inner._dispatch_compiled(  # pyright: ignore[reportPrivateUsage]
                GET_READ, compiled_write
            )
        assert calls == 0

    def test_compiled_dispatch_is_not_exposed_by_read_only_executor(self) -> None:
        executor = ReadOnlyExecutor(make_executor(lambda request: httpx.Response(200, json=[])))
        assert not hasattr(executor, "dispatch_compiled")
