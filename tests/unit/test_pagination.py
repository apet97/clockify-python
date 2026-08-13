"""Pagination stop-rule tests."""

import httpx
import pytest

from clockify.pagination import (
    Page,
    PaginationIncompleteError,
    PaginationLoopError,
    iter_all,
    iter_pages,
)
from clockify.response import ClockifyResponse


def page(items: list[str], number: int, *, size: int = 2, last: bool | None = None) -> Page[str]:
    return Page(items=items, page=number, page_size=size, last_page=last)


def fetcher(pages: dict[int, Page[str]]):  # type: ignore[no-untyped-def]
    async def fetch(n: int) -> Page[str]:
        return pages[n]

    return fetch


async def test_empty_page_stops() -> None:
    items = await iter_all(fetcher({1: page([], 1)}))
    assert items == []


async def test_last_page_true_stops_even_when_full() -> None:
    items = await iter_all(fetcher({1: page(["a", "b"], 1, last=True)}))
    assert items == ["a", "b"]


async def test_last_page_false_continues_after_short_page() -> None:
    pages = {1: page(["a"], 1, last=False), 2: page(["b"], 2, last=True)}
    items = await iter_all(fetcher(pages))
    assert items == ["a", "b"]


async def test_short_page_without_header_stops() -> None:
    items = await iter_all(fetcher({1: page(["a"], 1)}))
    assert items == ["a"]


async def test_full_page_without_header_continues() -> None:
    pages = {1: page(["a", "b"], 1), 2: page(["c"], 2)}
    items = await iter_all(fetcher(pages))
    assert items == ["a", "b", "c"]


async def test_repeated_page_raises_loop_error() -> None:
    pages = {1: page(["a", "b"], 1), 2: page(["a", "b"], 2)}
    with pytest.raises(PaginationLoopError):
        await iter_all(fetcher(pages))


async def test_max_pages_raises_incomplete_with_partial_items() -> None:
    pages = {
        1: page(["a", "b"], 1, last=False),
        2: page(["c", "d"], 2, last=False),
        3: page(["e", "f"], 3, last=False),
    }
    with pytest.raises(PaginationIncompleteError) as info:
        await iter_all(fetcher(pages), max_pages=2)
    assert info.value.items == ["a", "b", "c", "d"]
    assert info.value.pages_fetched == 2


async def test_iter_pages_yields_page_objects() -> None:
    pages = {1: page(["a"], 1, last=True)}
    seen = [p async for p in iter_pages(fetcher(pages))]
    assert len(seen) == 1
    assert seen[0].items == ["a"]


def test_page_from_response_preserves_transport_metadata() -> None:
    response = ClockifyResponse(
        data=["a"],
        status_code=200,
        headers=httpx.Headers({"Last-Page": "false", "X-Request-Id": "req-1"}),
        request_id="req-1",
        operation_id="listItems",
    )

    result = Page.from_response(response, items=["a"], page=1, page_size=2)

    assert result.items == ["a"]
    assert result.last_page is False
    assert result.request_id == "req-1"
    assert result.headers is response.headers


def test_page_from_response_accepts_adapted_items() -> None:
    response = ClockifyResponse(
        data=[{"id": "a"}],
        status_code=200,
        headers=httpx.Headers(),
        request_id=None,
        operation_id="listItems",
    )

    result = Page.from_response(response, items=["a"], page=1, page_size=2, count=1)

    assert result.items == ["a"]
    assert result.last_page is None
    assert result.count == 1
