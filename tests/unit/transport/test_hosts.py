"""Final destination validation tests."""

import pytest

from clockify._transport.hosts import validate_destination
from clockify.config import DEFAULT_SERVICE_URLS
from clockify.errors import ClockifyConfigurationError
from clockify.operations.model import Service


def validate_regular(url: str, *, base: str | None = None) -> None:
    service_urls = dict(DEFAULT_SERVICE_URLS)
    if base is not None:
        service_urls[Service.REGULAR] = base
    validate_destination(
        url,
        service=Service.REGULAR,
        service_urls=service_urls,
        default_urls=DEFAULT_SERVICE_URLS,
        allow_custom_hosts=base is not None,
    )


def test_path_must_be_inside_a_complete_base_segment() -> None:
    with pytest.raises(ClockifyConfigurationError, match="escapes service base"):
        validate_regular("https://api.clockify.me/api/v10/workspaces")


def test_child_path_is_allowed() -> None:
    validate_regular("https://api.clockify.me/api/v1/workspaces")


@pytest.mark.parametrize(
    ("base", "url", "message"),
    [
        (
            "http://self-hosted.example.com/api/v1",
            "http://self-hosted.example.com/api/v1/workspaces",
            "HTTPS",
        ),
        (
            "https://user:password@self-hosted.example.com/api/v1",
            "https://user:password@self-hosted.example.com/api/v1/workspaces",
            "user information",
        ),
    ],
)
def test_unsafe_custom_service_url_is_rejected(base: str, url: str, message: str) -> None:
    with pytest.raises(ClockifyConfigurationError, match=message):
        validate_regular(url, base=base)
