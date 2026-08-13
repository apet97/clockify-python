"""Client configuration defaults."""

import math
from dataclasses import dataclass

import httpx

from clockify.operations.model import Service

DEFAULT_SERVICE_URLS: dict[Service, str] = {
    Service.REGULAR: "https://api.clockify.me/api/v1",
    Service.REPORTS: "https://reports.api.clockify.me/v1",
    Service.AUDIT_LOG: "https://auditlog-api.api.clockify.me/v1",
}

# Sane API-client defaults; callers can replace globally or per call.
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=10.0)

USER_AGENT = "clockify-python-115/0.2.0"


def _valid_attempt_count(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and value >= 1


def _valid_delay(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
        and value >= 0
    )


@dataclass(frozen=True, slots=True)
class ReadRetryPolicy:
    """Optional retry for non-mutating operations only.

    Enforced at the executor boundary: a mutating operation is attempted exactly
    once even when this policy is configured.
    """

    max_attempts: int = 3
    base_delay: float = 0.5
    max_delay: float = 8.0

    def __post_init__(self) -> None:
        if not _valid_attempt_count(self.max_attempts):
            raise ValueError("max_attempts must be >= 1")
        for name, value in (("base_delay", self.base_delay), ("max_delay", self.max_delay)):
            if not _valid_delay(value):
                raise ValueError(f"{name} must be a finite number >= 0")


RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
