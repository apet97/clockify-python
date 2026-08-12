"""Response decoding by declared `ResponseKind` and actual content type."""

import json
import re
from typing import Any

import httpx

from clockify.errors import (
    ClockifyAPIError,
    ClockifyAuthenticationError,
    ClockifyConflictError,
    ClockifyNotFoundError,
    ClockifyPermissionError,
    ClockifyRateLimitError,
    ClockifyResponseValidationError,
)
from clockify.operations.model import Operation, ResponseKind
from clockify.response import BinaryResponse, TextResponse

_FILENAME = re.compile(r'filename="?([^";]+)"?', re.IGNORECASE)


def request_id_of(response: httpx.Response) -> str | None:
    return response.request.headers.get("X-Request-Id")


def _filename_of(response: httpx.Response) -> str | None:
    disposition = response.headers.get("Content-Disposition", "")
    match = _FILENAME.search(disposition)
    return match.group(1) if match else None


def _decode_json(operation: Operation, response: httpx.Response) -> Any:
    if not response.content:
        return None
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError) as exc:
        raise ClockifyResponseValidationError(
            f"{operation.operation_id}: 2xx response body is not valid JSON",
            operation_id=operation.operation_id,
            request_id=request_id_of(response),
        ) from exc


def _decode_text(response: httpx.Response) -> TextResponse:
    # httpx decodes with the response charset, defaulting to UTF-8.
    return TextResponse(
        text=response.text,
        content_type=response.headers.get("Content-Type", ""),
        status_code=response.status_code,
        headers=response.headers,
        request_id=request_id_of(response),
    )


def _decode_bytes(response: httpx.Response) -> BinaryResponse:
    return BinaryResponse(
        content=response.content,
        content_type=response.headers.get("Content-Type", "application/octet-stream"),
        filename=_filename_of(response),
        status_code=response.status_code,
        headers=response.headers,
        request_id=request_id_of(response),
    )


def decode_success(operation: Operation, response: httpx.Response) -> Any:
    kind = operation.response_kind
    if kind is ResponseKind.JSON:
        return _decode_json(operation, response)
    if kind is ResponseKind.BYTES:
        return _decode_bytes(response)
    if kind is ResponseKind.TEXT:
        return _decode_text(response)
    if kind is ResponseKind.NONE:
        return None
    # CONTENT_NEGOTIATED: choose by the actual Content-Type. Unknown binary
    # content stays bytes; nothing is lossily re-decoded as text.
    content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
    if content_type in ("application/json", "application/problem+json"):
        return _decode_json(operation, response)
    if content_type.startswith("text/"):
        return _decode_text(response)
    return _decode_bytes(response)


def parse_retry_after(response: httpx.Response) -> float | None:
    raw = response.headers.get("Retry-After")
    if raw is None:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if value >= 0 else None


_ERROR_BY_STATUS: dict[int, type[ClockifyAPIError]] = {
    401: ClockifyAuthenticationError,
    403: ClockifyPermissionError,
    404: ClockifyNotFoundError,
    405: ClockifyConflictError,
    409: ClockifyConflictError,
    429: ClockifyRateLimitError,
}


def raise_api_error(operation: Operation, response: httpx.Response) -> "None":
    body: Any = None
    message: str | None = None
    api_code: int | str | None = None
    try:
        body = response.json()
        if isinstance(body, dict):
            message = body.get("message") or body.get("description")
            api_code = body.get("code")
    except (json.JSONDecodeError, ValueError):
        text = response.text
        message = text[:500] if text else None

    error_class = _ERROR_BY_STATUS.get(response.status_code, ClockifyAPIError)
    raise error_class(
        f"{operation.operation_id}: HTTP {response.status_code}"
        + (f" — {message}" if message else ""),
        operation_id=operation.operation_id,
        status_code=response.status_code,
        body=body,
        api_code=api_code,
        request_id=request_id_of(response),
        retry_after=parse_retry_after(response),
        headers=response.headers,
    )
