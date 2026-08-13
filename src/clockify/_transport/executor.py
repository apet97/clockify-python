"""The single HTTP execution boundary for every Clockify operation."""

import asyncio
import random
import uuid
from typing import Any

import httpx

from clockify._transport.auth import Credential
from clockify._transport.decode import (
    build_api_error,
    decode_success,
    parse_retry_after,
    request_id_of,
    sanitize_error_text,
)
from clockify._transport.encode import CompiledRequest, compile_request
from clockify._transport.hosts import validate_destination
from clockify.config import (
    DEFAULT_SERVICE_URLS,
    RETRYABLE_STATUS_CODES,
    USER_AGENT,
    ReadRetryPolicy,
)
from clockify.errors import (
    ClockifyConfigurationError,
    ClockifyTransportError,
    MutationOutcomeUnknownError,
)
from clockify.files import Upload
from clockify.operations.model import Operation, Service
from clockify.operations.registry import BY_ID
from clockify.response import ClockifyResponse

_PROTECTED_CALLER_HEADERS = frozenset({"host", ":authority", "x-api-key", "x-addon-token"})


def _reject_protected_headers(headers: dict[str, str]) -> None:
    protected = sorted(name for name in headers if name.lower() in _PROTECTED_CALLER_HEADERS)
    if protected:
        raise ClockifyConfigurationError(
            "caller supplied protected header(s): " + ", ".join(protected)
        )


def _canonical_operation(operation: Operation) -> Operation:
    canonical = BY_ID.get(operation.operation_id)
    if canonical is None:
        raise ClockifyConfigurationError(f"unknown Clockify operation {operation.operation_id!r}")
    if operation != canonical:
        raise ClockifyConfigurationError(
            f"operation {operation.operation_id!r} does not match the operation registry"
        )
    return canonical


def _validate_client_defaults(client: httpx.AsyncClient) -> None:
    if client.params:
        raise ClockifyConfigurationError("the injected HTTP client must not define parameters")
    if client.auth is not None:
        raise ClockifyConfigurationError("the injected HTTP client must not define authentication")
    if client.event_hooks.get("request"):
        raise ClockifyConfigurationError("the injected HTTP client must not define request hooks")
    _reject_protected_headers(dict(client.headers))


def _validate_effective_request(request: httpx.Request) -> None:
    credential_headers = sorted(
        name
        for name in request.headers
        if name.lower() in {":authority", "x-api-key", "x-addon-token"}
    )
    if credential_headers:
        raise ClockifyConfigurationError(
            "the effective HTTP request contained protected header(s): "
            + ", ".join(credential_headers)
        )
    expected_host = request.url.netloc.decode("ascii")
    if request.headers.get("Host", "").lower() != expected_host.lower():
        raise ClockifyConfigurationError("the effective HTTP request has an invalid Host header")


class HttpExecutor:
    """Compiles, authenticates, dispatches, and decodes exactly one operation call.

    Owns no event loop and performs no caching. Redirects are disabled; a 3xx
    becomes an API error and credentials never travel to another host.
    """

    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        credential: Credential,
        service_urls: dict[Service, str] | None = None,
        allow_custom_hosts: bool = False,
        retry_policy: ReadRetryPolicy | None = None,
    ) -> None:
        self._client = client
        self._credential = credential
        self._service_urls = dict(DEFAULT_SERVICE_URLS)
        if service_urls:
            self._service_urls.update(service_urls)
        self._allow_custom_hosts = allow_custom_hosts
        self._retry_policy = retry_policy

    def compile(
        self,
        operation: Operation,
        *,
        path_args: dict[str, str],
        query: dict[str, Any] | None = None,
        body: Any = None,
        files: dict[str, Upload] | None = None,
        headers: dict[str, str] | None = None,
    ) -> CompiledRequest:
        """Pure compilation without auth. Reused by the MCP write-plan binding."""
        operation = _canonical_operation(operation)
        caller_headers = headers or {}
        _reject_protected_headers(caller_headers)
        default_headers = {
            "User-Agent": USER_AGENT,
            "X-Request-Id": str(uuid.uuid4()),
        }
        # Caller headers win over defaults.
        merged = {**default_headers, **caller_headers}
        return compile_request(
            operation,
            base_url=self._service_urls[operation.service],
            path_args=path_args,
            query=query or {},
            body=body,
            files=files,
            headers=merged,
        )

    async def execute(
        self,
        operation: Operation,
        *,
        path_args: dict[str, str],
        query: dict[str, Any] | None = None,
        body: Any = None,
        files: dict[str, Upload] | None = None,
        headers: dict[str, str] | None = None,
        timeout: httpx.Timeout | None = None,
    ) -> ClockifyResponse[Any]:
        compiled = self.compile(
            operation, path_args=path_args, query=query, body=body, files=files, headers=headers
        )
        return await self._dispatch_compiled(operation, compiled, timeout=timeout)

    async def _dispatch_compiled(
        self,
        operation: Operation,
        compiled: CompiledRequest,
        *,
        timeout: httpx.Timeout | None = None,
    ) -> ClockifyResponse[Any]:
        operation = _canonical_operation(operation)
        if compiled.operation_id != operation.operation_id:
            raise ClockifyConfigurationError(
                f"compiled request operation {compiled.operation_id!r} does not match "
                f"{operation.operation_id!r}"
            )
        if compiled.method != operation.http_method:
            raise ClockifyConfigurationError(
                f"compiled request method does not match {operation.operation_id!r}"
            )
        _reject_protected_headers(dict(compiled.headers))

        retryable = self._retry_policy is not None and not operation.semantics.mutates
        attempts = self._retry_policy.max_attempts if retryable and self._retry_policy else 1

        last_error: Exception | None = None
        for attempt in range(attempts):
            request = self._build_request(operation, compiled, timeout)
            response: httpx.Response | None = None
            transport_error: ClockifyTransportError | None = None
            write_cancelled = False
            try:
                response = await self._client.send(
                    request,
                    auth=None,
                    follow_redirects=False,
                )
            except asyncio.CancelledError:
                if operation.semantics.mutates:
                    write_cancelled = True
                else:
                    raise
            except httpx.TransportError as exc:
                transport_error = self._transport_error(operation, exc)

            if write_cancelled:
                raise MutationOutcomeUnknownError(
                    f"{operation.operation_id}: request cancellation after dispatch; "
                    "read state back before any manual retry",
                    operation_id=operation.operation_id,
                ) from None
            if transport_error is not None:
                last_error = transport_error
                if not retryable or attempt == attempts - 1:
                    raise last_error from None
                await self._sleep(attempt, None)
                continue

            assert response is not None
            can_retry_status = (
                retryable
                and response.status_code in RETRYABLE_STATUS_CODES
                and attempt < attempts - 1
            )
            if can_retry_status:
                retry_after = parse_retry_after(response)
                await response.aclose()
                await self._sleep(attempt, retry_after)
                continue
            if 200 <= response.status_code < 300:
                data = decode_success(operation, response)
                return ClockifyResponse(
                    data=data,
                    status_code=response.status_code,
                    headers=response.headers,
                    request_id=request_id_of(response),
                    operation_id=operation.operation_id,
                )
            raise build_api_error(
                operation, response, sensitive_values=self._credential.sensitive_values()
            ) from None
        raise last_error or ClockifyTransportError(
            f"{operation.operation_id}: retry loop exhausted", operation_id=operation.operation_id
        )

    def _build_request(
        self,
        operation: Operation,
        compiled: CompiledRequest,
        timeout: httpx.Timeout | None,
    ) -> httpx.Request:
        _validate_client_defaults(self._client)
        files_arg: list[Any] | None = None
        if compiled.files or compiled.form_data is not None:
            # Multipart operation. Form fields ride as filename-less parts so the
            # encoding stays multipart/form-data even with no file attached.
            files_arg = list(compiled.files)
            for field_name, field_value in compiled.form_data or ():
                files_arg.append((field_name, (None, field_value)))

        request_kwargs: dict[str, Any] = {
            "params": list(compiled.params) or None,
            "json": compiled.json_body,
            "files": files_arg,
            "headers": compiled.headers,
        }
        if timeout is not None:
            request_kwargs["timeout"] = timeout
        request = self._client.build_request(
            compiled.method,
            compiled.url,
            **request_kwargs,
        )
        expected_url = httpx.URL(compiled.url).copy_merge_params(compiled.params)
        if request.url != expected_url:
            raise ClockifyConfigurationError(
                "the effective HTTP request URL differs from the compiled request"
            )
        _validate_effective_request(request)
        # Validate the fully merged destination before credentials are attached.
        validate_destination(
            str(request.url),
            service=operation.service,
            service_urls=self._service_urls,
            default_urls=DEFAULT_SERVICE_URLS,
            allow_custom_hosts=self._allow_custom_hosts,
        )
        credential_headers: dict[str, str] = {}
        self._credential.attach(credential_headers)
        request.headers.update(credential_headers)
        return request

    def _transport_error(
        self, operation: Operation, exc: httpx.TransportError
    ) -> ClockifyTransportError:
        if operation.semantics.mutates and not isinstance(
            exc, (httpx.ConnectError, httpx.ConnectTimeout)
        ):
            # The request may have reached Clockify. Outcome is unknowable here.
            return MutationOutcomeUnknownError(
                f"{operation.operation_id}: transport failure after dispatch; "
                "read state back before any manual retry",
                operation_id=operation.operation_id,
            )
        return ClockifyTransportError(
            sanitize_error_text(
                f"{operation.operation_id}: {exc.__class__.__name__}: {exc}",
                sensitive_values=self._credential.sensitive_values(),
            ),
            operation_id=operation.operation_id,
        )

    async def _sleep(self, attempt: int, retry_after: float | None) -> None:
        policy = self._retry_policy
        assert policy is not None
        if retry_after is not None:
            delay = min(retry_after, policy.max_delay)
        else:
            delay = min(policy.base_delay * (2**attempt), policy.max_delay)
            delay *= 0.5 + random.random() / 2  # jitter
        await asyncio.sleep(delay)


class ReadOnlyExecutor:
    """Final-boundary wrapper that refuses every mutating operation.

    This class — not tool registration or annotations — is the MCP read
    security boundary.
    """

    def __init__(self, inner: HttpExecutor) -> None:
        self._inner = inner

    def compile(self, operation: Operation, **kwargs: Any) -> CompiledRequest:
        operation = self._require_read(operation)
        return self._inner.compile(operation, **kwargs)

    async def execute(self, operation: Operation, **kwargs: Any) -> ClockifyResponse[Any]:
        operation = self._require_read(operation)
        return await self._inner.execute(operation, **kwargs)

    @staticmethod
    def _require_read(operation: Operation) -> Operation:
        from clockify.errors import ClockifyReadOnlyViolation

        operation = _canonical_operation(operation)
        if operation.semantics.mutates:
            raise ClockifyReadOnlyViolation(
                f"{operation.operation_id} mutates Clockify state and was blocked "
                "by the read-only execution boundary"
            )
        return operation
