"""Foundation units: error codes, receipts, paging, name resolution, SSRF guard."""

from typing import Any

import pytest

from clockify.errors import (
    ClockifyAPIError,
    ClockifyConfigurationError,
    ClockifyRateLimitError,
    ClockifyTransportError,
    MutationOutcomeUnknownError,
)
from clockify_mcp.error_codes import CODES, classify_error, is_retryable
from clockify_mcp.errors import ToolError
from clockify_mcp.paging import PaginationError, collect_paged
from clockify_mcp.receipt import error_receipt, success_receipt
from clockify_mcp.resolve import AmbiguousNameError, resolve_by_name
from clockify_mcp.webhook_url import assert_safe_webhook_url


def api_error(status_code: int, detail: str = "", api_code: int | None = None) -> ClockifyAPIError:
    return ClockifyAPIError(
        f"HTTP {status_code}",
        status_code=status_code,
        operation_id="op",
        detail=detail,
        api_code=api_code,
    )


class TestErrorCodes:
    def test_seventeen_codes(self) -> None:
        assert len(CODES) == 17

    @pytest.mark.parametrize(
        ("exc", "code"),
        [
            (api_error(400), "invalid_request"),
            (api_error(401), "auth_or_permission"),
            (api_error(402), "feature_unavailable"),
            (api_error(403), "auth_or_permission"),
            (api_error(404), "not_found"),
            (api_error(405), "dead_route"),
            (api_error(409), "conflict"),
            (api_error(502), "clockify_upstream_error"),
            (
                api_error(400, detail="entity must be archived first"),
                "active_resource_delete_blocked",
            ),
            (api_error(400, detail="addon-rejected"), "addon_token_restricted"),
            (ClockifyTransportError("boom"), "connection_error"),
            (MutationOutcomeUnknownError("?"), "connection_error"),
            (ClockifyConfigurationError("no credential"), "setup_required"),
            (ValueError("odd"), "error"),
        ],
    )
    def test_classification(self, exc: BaseException, code: str) -> None:
        assert classify_error(exc) == code

    def test_rate_limit_variants(self) -> None:
        with_delay = ClockifyRateLimitError(
            "429", status_code=429, operation_id="op", retry_after=3.0
        )
        without = ClockifyRateLimitError("429", status_code=429, operation_id="op")
        assert classify_error(with_delay) == "rate_limited_retry_after"
        assert classify_error(without) == "rate_limited"
        assert is_retryable("rate_limited") is True
        assert is_retryable("invalid_request") is False


class TestReceipt:
    def test_success_shape(self) -> None:
        receipt = success_receipt("tags.create", entity="tag", ids={"tagId": "a" * 24})
        assert receipt.ok is True
        assert receipt.error is None

    def test_error_carries_code_and_recovery(self) -> None:
        receipt = error_receipt("tags.create", api_error(404))
        assert receipt.ok is False
        assert receipt.error is not None and receipt.error.code == "not_found"
        assert receipt.recovery is not None and receipt.recovery.retryable is False


class TestPaging:
    async def test_collects_until_short_page(self) -> None:
        pages = {1: [{"id": "a"}, {"id": "b"}], 2: [{"id": "c"}]}

        async def fetch(page: int) -> tuple[list[Any], bool | None]:
            return pages.get(page, []), None

        items = await collect_paged(fetch, page_size=2)
        assert [item["id"] for item in items] == ["a", "b", "c"]

    async def test_last_page_header_stops(self) -> None:
        calls: list[int] = []

        async def fetch(page: int) -> tuple[list[Any], bool | None]:
            calls.append(page)
            return [{"id": f"x{page}"}], True

        await collect_paged(fetch, page_size=1)
        assert calls == [1]

    async def test_repeated_page_raises(self) -> None:
        async def fetch(page: int) -> tuple[list[Any], bool | None]:
            return [{"id": "same"}], None

        with pytest.raises(PaginationError, match="repeated"):
            await collect_paged(fetch, page_size=1)

    async def test_max_pages_refuses_partial(self) -> None:
        async def fetch(page: int) -> tuple[list[Any], bool | None]:
            return [{"id": f"p{page}"}], None

        with pytest.raises(PaginationError, match="exceeded"):
            await collect_paged(fetch, page_size=1, max_pages=3)


class TestResolve:
    @staticmethod
    def fetcher(items: list[dict[str, str]]):
        async def fetch(page: int) -> tuple[list[Any], bool | None]:
            return (items, True) if page == 1 else ([], True)

        return fetch

    async def test_hex_id_short_circuits(self) -> None:
        async def fetch(page: int) -> tuple[list[Any], bool | None]:
            raise AssertionError("must not list when an id is supplied")

        value = "a" * 24
        assert await resolve_by_name(value, label="project", fetch=fetch) == value

    async def test_exact_case_insensitive_match(self) -> None:
        fetch = self.fetcher([{"id": "1" * 24, "name": "Internal"}])
        assert await resolve_by_name("internal", label="project", fetch=fetch) == "1" * 24

    async def test_ambiguity_carries_candidates(self) -> None:
        fetch = self.fetcher([{"id": "1" * 24, "name": "Dup"}, {"id": "2" * 24, "name": "dup"}])
        with pytest.raises(AmbiguousNameError) as info:
            await resolve_by_name("dup", label="tag", fetch=fetch)
        assert {c.id for c in info.value.candidates} == {"1" * 24, "2" * 24}

    async def test_absence_is_actionable(self) -> None:
        with pytest.raises(ToolError, match="not found"):
            await resolve_by_name("ghost", label="client", fetch=self.fetcher([]))


class TestWebhookUrl:
    @pytest.mark.parametrize(
        "url",
        [
            "http://example.com/hook",
            "https://localhost/hook",
            "https://127.0.0.1/hook",
            "https://10.0.0.8/hook",
            "https://169.254.169.254/latest/meta-data",
            "https://metadata.google.internal/x",
            "https://[::1]/hook",
        ],
    )
    def test_rejects_unsafe(self, url: str) -> None:
        with pytest.raises(ToolError):
            assert_safe_webhook_url(url)

    def test_accepts_public_https(self) -> None:
        assert_safe_webhook_url("https://hooks.example.com/clockify")
