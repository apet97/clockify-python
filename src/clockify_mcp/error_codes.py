"""Stable tool error codes and the classifier that assigns them.

Seventeen codes, ported from the TS MCP's registry so agents can key retry
and recovery decisions on a stable vocabulary. Classification prefers
structured evidence (exception type, HTTP status, API code) and falls back to
a short ordered message-pattern ladder only where the wire gives no better
signal.
"""

import asyncio
import re
from dataclasses import dataclass

from clockify.errors import (
    ClockifyAPIError,
    ClockifyConfigurationError,
    ClockifyRateLimitError,
    ClockifyReadOnlyViolation,
    ClockifyTransportError,
    MutationOutcomeUnknownError,
)


@dataclass(frozen=True, slots=True)
class CodeInfo:
    retryable: bool
    hint: str


CODES: dict[str, CodeInfo] = {
    "invalid_request": CodeInfo(False, "Fix the arguments shown in the message and retry."),
    "auth_or_permission": CodeInfo(False, "Check the credential and its workspace permissions."),
    "feature_unavailable": CodeInfo(False, "The workspace plan does not include this feature."),
    "not_found": CodeInfo(False, "Verify the id; list the resource to find a valid one."),
    "conflict": CodeInfo(False, "The entity conflicts with current state; re-read and adjust."),
    "rate_limited": CodeInfo(True, "Slow down and retry after a short pause."),
    "rate_limited_retry_after": CodeInfo(True, "Retry after the indicated delay."),
    "clockify_upstream_error": CodeInfo(True, "Clockify had a server-side problem; retry later."),
    "connection_error": CodeInfo(True, "Network problem reaching Clockify; retry."),
    "aborted": CodeInfo(True, "The request was cancelled before completion."),
    "addon_token_restricted": CodeInfo(
        False, "The addon token cannot call this endpoint; use an API key."
    ),
    "host_routing_required": CodeInfo(
        False, "This operation needs a different Clockify service host."
    ),
    "active_resource_delete_blocked": CodeInfo(
        False, "Archive the entity (or mark the task DONE) before deleting it."
    ),
    "dead_route": CodeInfo(False, "This route does not exist on the Clockify API."),
    "name_reserved_after_delete": CodeInfo(
        False, "The name stays reserved after deletion; pick a different name."
    ),
    "setup_required": CodeInfo(
        False,
        "Set exactly one of CLOCKIFY_API_KEY or CLOCKIFY_ADDON_TOKEN "
        "(and optionally CLOCKIFY_WORKSPACE_ID), then retry.",
    ),
    "error": CodeInfo(False, "Unclassified failure; read the message."),
}

_STATUS_CODES: dict[int, str] = {
    400: "invalid_request",
    401: "auth_or_permission",
    402: "feature_unavailable",
    403: "auth_or_permission",
    404: "not_found",
    405: "dead_route",
    409: "conflict",
    429: "rate_limited",
}

# Ordered: the first matching pattern wins. Only patterns with an observed
# wire signal live here; everything else classifies from structured data.
_MESSAGE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("addon_token_restricted", re.compile(r"addon.?token|addon-rejected", re.IGNORECASE)),
    ("active_resource_delete_blocked", re.compile(r"archiv|is active|DONE", re.IGNORECASE)),
    ("name_reserved_after_delete", re.compile(r"already exists|reserved", re.IGNORECASE)),
    ("clockify_upstream_error", re.compile(r"upstream|gateway|bad gateway", re.IGNORECASE)),
)


def classify_error(exc: BaseException) -> str:
    """Map any tool failure to one stable code."""
    if isinstance(exc, asyncio.CancelledError):
        return "aborted"
    if isinstance(exc, ClockifyConfigurationError):
        return "setup_required"
    if isinstance(exc, ClockifyReadOnlyViolation):
        return "invalid_request"
    if isinstance(exc, MutationOutcomeUnknownError):
        return "connection_error"
    if isinstance(exc, ClockifyRateLimitError):
        return "rate_limited_retry_after" if exc.retry_after is not None else "rate_limited"
    if isinstance(exc, ClockifyAPIError):
        message = f"{exc.detail or ''} {exc}"
        for code, pattern in _MESSAGE_PATTERNS:
            if pattern.search(message):
                return code
        if exc.status_code >= 500:
            return "clockify_upstream_error"
        return _STATUS_CODES.get(exc.status_code, "error")
    if isinstance(exc, ClockifyTransportError):
        return "connection_error"
    return "error"


def recovery_hint(code: str) -> str:
    return CODES[code].hint


def is_retryable(code: str) -> bool:
    return CODES[code].retryable
