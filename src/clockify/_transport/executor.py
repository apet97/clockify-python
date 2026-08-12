"""The single HTTP execution boundary for every Clockify operation."""

import asyncio
import random
import uuid
from typing import Any

import httpx

from clockify._transport.auth import Credential
from clockify._transport.decode import decode_success, raise_api_error, request_id_of
from clockify._transport.encode import CompiledRequest, compile_request
from clockify._transport.hosts import validate_destination
from clockify.config import (
    DEFAULT_SERVICE_URLS,
    DEFAULT_TIMEOUT,
    RETRYABLE_STATUS_CODES,
    USER_AGENT,
    ReadRetryPolicy,
)
from clockify.errors import (
    ClockifyTransportError,
    MutationOutcomeUnknownError,
)
from clockify.files import Upload
from clockify.operations.model import Operation, Service
from clockify.response import ClockifyResponse


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
        default_headers = {
            "User-Agent": USER_AGENT,
            "X-Request-Id": str(uuid.uuid4()),
        }
        # Caller headers win over defaults.
        merged = {**default_headers, **(headers or {})}
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
        return await self.dispatch_compiled(operation, compiled, timeout=timeout)

    async def dispatch_compiled(
        self,
        operation: Operation,
        compiled: CompiledRequest,
        *,
        timeout: httpx.Timeout | None = None,
    ) -> ClockifyResponse[Any]:
        # Final-destination validation happens before the credential is attached.
        validate_destination(
            compiled.url,
            service=operation.service,
            service_urls=self._service_urls,
            default_urls=DEFAULT_SERVICE_URLS,
            allow_custom_hosts=self._allow_custom_hosts,
        )
        headers = dict(compiled.headers)
        self._credential.attach(headers)

        retryable = self._retry_policy is not None and not operation.semantics.mutates
        attempts = self._retry_policy.max_attempts if retryable and self._retry_policy else 1

        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                response = await self._send(operation, compiled, headers, timeout)
            except asyncio.CancelledError:
                raise  # cancellation always propagates
            except httpx.TransportError as exc:
                last_error = self._transport_error(operation, exc)
                if not retryable or attempt == attempts - 1:
                    raise last_error from exc
                await self._sleep(attempt, None)
                continue

            can_retry_status = (
                retryable
                and response.status_code in RETRYABLE_STATUS_CODES
                and attempt < attempts - 1
            )
            if can_retry_status:
                retry_after = _retry_after_seconds(response)
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
            raise_api_error(operation, response)
        raise last_error or ClockifyTransportError(
            f"{operation.operation_id}: retry loop exhausted", operation_id=operation.operation_id
        )

    async def _send(
        self,
        operation: Operation,
        compiled: CompiledRequest,
        headers: dict[str, str],
        timeout: httpx.Timeout | None,
    ) -> httpx.Response:
        files_arg: list[Any] | None = None
        if compiled.files or compiled.form_data is not None:
            # Multipart operation. Form fields ride as filename-less parts so the
            # encoding stays multipart/form-data even with no file attached.
            files_arg = list(compiled.files)
            for field_name, field_value in compiled.form_data or ():
                files_arg.append((field_name, (None, field_value)))
        return await self._client.request(
            compiled.method,
            compiled.url,
            params=list(compiled.params) or None,
            json=compiled.json_body,
            files=files_arg,
            headers=headers,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
            follow_redirects=False,
        )

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
            f"{operation.operation_id}: {exc.__class__.__name__}: {exc}",
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
        self._require_read(operation)
        return self._inner.compile(operation, **kwargs)

    async def execute(self, operation: Operation, **kwargs: Any) -> ClockifyResponse[Any]:
        self._require_read(operation)
        return await self._inner.execute(operation, **kwargs)

    async def dispatch_compiled(
        self, operation: Operation, compiled: CompiledRequest, **kwargs: Any
    ) -> ClockifyResponse[Any]:
        self._require_read(operation)
        return await self._inner.dispatch_compiled(operation, compiled, **kwargs)

    @staticmethod
    def _require_read(operation: Operation) -> None:
        from clockify.errors import ClockifyReadOnlyViolation

        if operation.semantics.mutates:
            raise ClockifyReadOnlyViolation(
                f"{operation.operation_id} mutates Clockify state and was blocked "
                "by the read-only execution boundary"
            )


def _retry_after_seconds(response: httpx.Response) -> float | None:
    raw = response.headers.get("Retry-After")
    if raw is None:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if value >= 0 else None
