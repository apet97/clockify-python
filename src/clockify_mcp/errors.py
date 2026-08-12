"""SDK error -> safe, actionable MCP tool error conversion."""

from clockify.errors import (
    ClockifyAPIError,
    ClockifyConfigurationError,
    ClockifyError,
    ClockifyRateLimitError,
    ClockifyReadOnlyViolation,
    ClockifyTransportError,
)


class ToolError(Exception):
    """Raised inside tools; the MCP framework reports the message to the caller."""


def to_tool_error(exc: ClockifyError) -> ToolError:
    """Convert without leaking credentials (SDK errors never contain them)."""
    if isinstance(exc, ClockifyReadOnlyViolation):
        return ToolError(f"blocked: {exc}")
    if isinstance(exc, ClockifyRateLimitError):
        hint = f"; retry after {exc.retry_after}s" if exc.retry_after else ""
        return ToolError(f"Clockify rate limit hit{hint}")
    if isinstance(exc, ClockifyAPIError):
        return ToolError(f"Clockify API error {exc.status_code} on {exc.operation_id}: {exc}")
    if isinstance(exc, ClockifyConfigurationError):
        return ToolError(f"configuration problem: {exc}")
    if isinstance(exc, ClockifyTransportError):
        return ToolError(f"network problem reaching Clockify: {exc}")
    return ToolError(str(exc))
