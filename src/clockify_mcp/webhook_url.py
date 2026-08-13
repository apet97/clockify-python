"""Offline SSRF guard for webhook target URLs.

HTTPS only; refuses loopback, private, link-local, unique-local, unspecified,
and cloud-metadata destinations by literal address or well-known hostname.
Offline by design: no DNS resolution happens here, so DNS rebinding is out of
scope — the guard blocks what can be judged from the URL alone.
"""

import ipaddress
from urllib.parse import urlsplit

from clockify_mcp.errors import ToolError

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "metadata.google.internal",
        "metadata",
        "instance-data",
    }
)


def assert_safe_webhook_url(url: str) -> None:
    """Raise ToolError unless `url` is an acceptable public HTTPS endpoint."""
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise ToolError("webhook url must use https")
    hostname = parts.hostname
    if not hostname:
        raise ToolError("webhook url must include a host")
    lowered = hostname.lower().rstrip(".")
    if lowered in _BLOCKED_HOSTNAMES or lowered.endswith(".localhost"):
        raise ToolError(f"webhook url host {hostname!r} is not allowed")
    try:
        address = ipaddress.ip_address(lowered)
    except ValueError:
        return  # a hostname; DNS-based checks are deliberately out of scope
    if (
        address.is_loopback
        or address.is_private
        or address.is_link_local
        or address.is_reserved
        or address.is_multicast
        or address.is_unspecified
    ):
        raise ToolError(f"webhook url address {hostname!r} is not allowed")
