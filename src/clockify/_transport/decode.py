"""Response decoding by declared `ResponseKind` and actual content type."""

import json
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
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
_SENSITIVE_KEY = re.compile(
    r"(?:authorization|x[-_ ]?api[-_ ]?key|x[-_ ]?addon[-_ ]?token|"
    r"api[-_ ]?key|addon[-_ ]?token|access[-_ ]?token|password|secret|token)",
    re.IGNORECASE,
)
_SENSITIVE_PAIR = re.compile(
    r"(?i)\b(authorization|x-api-key|x-addon-token|api[_ -]?key|"
    r"addon[_ -]?token|access[_ -]?token|password|secret|token)"
    r"\b\s*[:=]\s*(?:bearer\s+)?(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)"
)
_MAX_ERROR_TEXT = 500
_MAX_BODY_BYTES = 4096
_MAX_COLLECTION_ITEMS = 20
_MAX_DEPTH = 4


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


def parse_retry_after(response: httpx.Response, *, now: datetime | None = None) -> float | None:
    """Parse RFC delay-seconds or HTTP-date relative to a deterministic clock."""
    raw = response.headers.get("Retry-After")
    if raw is None:
        return None
    try:
        value = float(raw)
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(raw)
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=UTC)
        reference = now
        if reference is None:
            date_header = response.headers.get("Date")
            if date_header:
                try:
                    reference = parsedate_to_datetime(date_header)
                except (TypeError, ValueError, OverflowError):
                    reference = None
            if reference is None:
                reference = datetime.now(UTC)
        if reference.tzinfo is None:
            reference = reference.replace(tzinfo=UTC)
        return max(0.0, (retry_at - reference).total_seconds())
    return value if value >= 0 else None


def _redact_text(value: str, sensitive_values: tuple[str, ...]) -> str:
    safe = value
    for secret in sensitive_values:
        if secret:
            safe = safe.replace(secret, "<redacted>")
    safe = _SENSITIVE_PAIR.sub(lambda match: f"{match.group(1)}: <redacted>", safe)
    if len(safe) > _MAX_ERROR_TEXT:
        return safe[: _MAX_ERROR_TEXT - 1] + "…"
    return safe


def _sanitize_value(value: Any, sensitive_values: tuple[str, ...], *, depth: int = 0) -> Any:
    if depth >= _MAX_DEPTH:
        return "<maximum depth reached>"
    if isinstance(value, str):
        return _redact_text(value, sensitive_values)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= _MAX_COLLECTION_ITEMS:
                result["<truncated>"] = f"{len(value) - _MAX_COLLECTION_ITEMS} more fields"
                break
            safe_key = _redact_text(str(key), ())
            result[safe_key] = (
                "<redacted>"
                if _SENSITIVE_KEY.fullmatch(str(key))
                else _sanitize_value(item, sensitive_values, depth=depth + 1)
            )
        return result
    if isinstance(value, (list, tuple)):
        items = [
            _sanitize_value(item, sensitive_values, depth=depth + 1)
            for item in value[:_MAX_COLLECTION_ITEMS]
        ]
        if len(value) > _MAX_COLLECTION_ITEMS:
            items.append(f"<{len(value) - _MAX_COLLECTION_ITEMS} more items>")
        return items
    return _redact_text(str(value), sensitive_values)


def _sanitize_body(value: Any, sensitive_values: tuple[str, ...]) -> Any:
    sanitized = _sanitize_value(value, sensitive_values)
    encoded = json.dumps(
        sanitized, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    if len(encoded) <= _MAX_BODY_BYTES:
        return sanitized
    return {"summary": f"upstream error body exceeded {_MAX_BODY_BYTES} bytes and was omitted"}


def _sanitize_headers(headers: httpx.Headers, sensitive_values: tuple[str, ...]) -> httpx.Headers:
    safe: dict[str, str] = {}
    for name, value in headers.items():
        safe[name] = (
            "<redacted>"
            if _SENSITIVE_KEY.fullmatch(name)
            else _redact_text(value, sensitive_values)
        )
    return httpx.Headers(safe)


_ERROR_BY_STATUS: dict[int, type[ClockifyAPIError]] = {
    401: ClockifyAuthenticationError,
    403: ClockifyPermissionError,
    404: ClockifyNotFoundError,
    405: ClockifyConflictError,
    409: ClockifyConflictError,
    429: ClockifyRateLimitError,
}


def raise_api_error(
    operation: Operation,
    response: httpx.Response,
    *,
    sensitive_values: tuple[str, ...] = (),
) -> "None":
    body: Any = None
    message: str | None = None
    api_code: int | str | None = None
    try:
        raw_body = response.json()
        body = _sanitize_body(raw_body, sensitive_values)
        if isinstance(raw_body, dict):
            raw_message = raw_body.get("message") or raw_body.get("description")
            if raw_message is not None:
                message = _redact_text(str(raw_message), sensitive_values)
            raw_code = raw_body.get("code")
            if isinstance(raw_code, (int, str)):
                api_code = _sanitize_value(raw_code, sensitive_values)
    except (json.JSONDecodeError, ValueError):
        text = response.text
        message = _redact_text(text, sensitive_values) if text else None

    error_class = _ERROR_BY_STATUS.get(response.status_code, ClockifyAPIError)
    raise error_class(
        f"{operation.operation_id}: HTTP {response.status_code}"
        + (f" — {message}" if message else ""),
        operation_id=operation.operation_id,
        status_code=response.status_code,
        body=body,
        detail=message,
        api_code=api_code,
        request_id=request_id_of(response),
        retry_after=parse_retry_after(response),
        headers=_sanitize_headers(response.headers, sensitive_values),
    )
