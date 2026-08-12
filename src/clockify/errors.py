"""Public SDK error hierarchy.

Broad, stable categories that preserve upstream detail. There is deliberately no
per-status or per-message subclass zoo.
"""

from typing import Any

import httpx


class ClockifyError(Exception):
    """Base class for every error this SDK raises deliberately."""


class ClockifyConfigurationError(ClockifyError):
    """Client construction or call configuration is invalid (no network involved)."""


class ClockifyTransportError(ClockifyError):
    """The HTTP exchange itself failed (connect, timeout, protocol)."""

    def __init__(self, message: str, *, operation_id: str | None = None) -> None:
        super().__init__(message)
        self.operation_id = operation_id


class MutationOutcomeUnknownError(ClockifyTransportError):
    """A mutating request was dispatched but its outcome could not be observed.

    Clockify may or may not have applied the change. Read the current state back
    before any manual retry; this SDK never retries a mutation for you.
    """


class ClockifyResponseValidationError(ClockifyError):
    """A 2xx response body did not match the declared response model."""

    def __init__(self, message: str, *, operation_id: str, request_id: str | None) -> None:
        super().__init__(message)
        self.operation_id = operation_id
        self.request_id = request_id


class ClockifyReadOnlyViolation(ClockifyError):
    """A mutating operation reached a read-only execution boundary."""


class ClockifyLifecycleError(ClockifyError):
    """A documented lifecycle prerequisite (archive/DONE/pending) is not satisfied."""


class ClockifyAPIError(ClockifyError):
    """Clockify answered with a non-2xx status."""

    def __init__(
        self,
        message: str,
        *,
        operation_id: str,
        status_code: int,
        body: Any = None,
        api_code: int | str | None = None,
        request_id: str | None = None,
        retry_after: float | None = None,
        headers: httpx.Headers | None = None,
    ) -> None:
        super().__init__(message)
        self.operation_id = operation_id
        self.status_code = status_code
        self.body = body
        self.api_code = api_code
        self.request_id = request_id
        self.retry_after = retry_after
        self.headers = headers


class ClockifyAuthenticationError(ClockifyAPIError):
    """401: the configured credential was rejected."""


class ClockifyPermissionError(ClockifyAPIError):
    """403: the credential lacks permission or the plan lacks the feature."""


class ClockifyNotFoundError(ClockifyAPIError):
    """404: the entity or route does not exist."""


class ClockifyConflictError(ClockifyAPIError):
    """405/409: state conflict, such as deleting an unarchived entity."""


class ClockifyRateLimitError(ClockifyAPIError):
    """429: rate limited; `retry_after` carries the server hint when present."""
