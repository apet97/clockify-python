"""Final-destination validation. Credentials attach only after this passes."""

import httpx

from clockify.errors import ClockifyConfigurationError
from clockify.operations.model import Service


def validate_destination(
    url: str,
    *,
    service: Service,
    service_urls: dict[Service, str],
    default_urls: dict[Service, str],
    allow_custom_hosts: bool,
) -> None:
    """Reject any final URL that is not inside the selected service base.

    A custom (non-default) service URL is honored only with the explicit
    `allow_custom_hosts=True` opt-in given at client construction.
    """
    base = service_urls[service]
    if base != default_urls[service] and not allow_custom_hosts:
        raise ClockifyConfigurationError(
            f"custom service URL {base!r} requires allow_custom_hosts=True"
        )
    parsed = httpx.URL(url)
    parsed_base = httpx.URL(base)
    if parsed.scheme != "https" or parsed_base.scheme != "https":
        raise ClockifyConfigurationError("Clockify service URLs must use HTTPS")
    if parsed.userinfo or parsed_base.userinfo:
        raise ClockifyConfigurationError("Clockify service URLs must not contain user information")
    if parsed.host != parsed_base.host or parsed.port != parsed_base.port:
        raise ClockifyConfigurationError(f"destination host mismatch: {parsed.host!r}")
    base_path = parsed_base.path.rstrip("/") or "/"
    path_is_inside_base = (
        base_path == "/" or parsed.path == base_path or parsed.path.startswith(base_path + "/")
    )
    if not path_is_inside_base:
        raise ClockifyConfigurationError(f"destination path escapes service base: {parsed.path!r}")
