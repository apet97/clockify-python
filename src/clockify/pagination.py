"""Typed pages and explicit pagination iteration.

Resource list methods stay plain page fetchers; these free functions loop them.
"""

from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

import httpx

from clockify.errors import ClockifyError

T = TypeVar("T")


class PaginationLoopError(ClockifyError):
    """The API returned an identical non-empty page twice; iteration would never end."""


class PaginationIncompleteError(ClockifyError):
    """`max_pages` was hit while more data remained. Results are NOT complete."""

    def __init__(self, message: str, items: list, pages_fetched: int) -> None:  # type: ignore[type-arg]
        super().__init__(message)
        self.items = items
        self.pages_fetched = pages_fetched


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: list[T]
    page: int
    page_size: int
    last_page: bool | None
    count: int | None = None
    request_id: str | None = None
    headers: httpx.Headers | None = None


PageFetcher = Callable[[int], Awaitable[Page[T]]]


async def iter_pages(
    fetch_page: PageFetcher[T],
    *,
    start_page: int = 1,
    max_pages: int | None = None,
) -> AsyncIterator[Page[T]]:
    """Yield pages until a proven stop condition.

    Stop rules in order: empty page; `Last-Page: true`; short page without a
    valid header (`Last-Page: false` overrides and continues); identical
    repeated non-empty page raises PaginationLoopError; `max_pages` raises
    PaginationIncompleteError rather than silently truncating.
    """
    page_number = start_page
    pages_fetched = 0
    previous_items: list[T] | None = None
    while True:
        page = await fetch_page(page_number)
        pages_fetched += 1
        if page.items and page.items == previous_items:
            raise PaginationLoopError(
                f"page {page_number} repeated the previous page's {len(page.items)} items"
            )
        yield page
        if not page.items:
            return
        if page.last_page is True:
            return
        if page.last_page is None and len(page.items) < page.page_size:
            return
        if max_pages is not None and pages_fetched >= max_pages:
            raise PaginationIncompleteError(
                f"stopped after max_pages={max_pages} with more data remaining",
                items=[],
                pages_fetched=pages_fetched,
            )
        previous_items = page.items
        page_number += 1


async def iter_all(
    fetch_page: PageFetcher[T],
    *,
    start_page: int = 1,
    max_pages: int | None = None,
) -> list[T]:
    """Collect every item. On max_pages overflow the partial items ride the error."""
    items: list[T] = []
    try:
        async for page in iter_pages(fetch_page, start_page=start_page, max_pages=max_pages):
            items.extend(page.items)
    except PaginationIncompleteError as exc:
        raise PaginationIncompleteError(
            str(exc), items=items, pages_fetched=exc.pages_fetched
        ) from None
    return items
