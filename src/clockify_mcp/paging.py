"""Full-list collection over paginated reads.

Clockify list endpoints paginate; several features (name resolution, demo
cleanup discovery, review windows) are wrong unless they walk every page.
``collect_paged`` walks pages until the authoritative ``Last-Page`` header
(when the endpoint sends one), an empty or short page, or a hard cap. It
refuses to return a silently partial result: cap exhaustion and repeated
identical pages raise instead.
"""

from collections.abc import Awaitable, Callable
from typing import Any

MAX_PAGES = 1000
DEFAULT_PAGE_SIZE = 200

# fetch(page) -> (items, last_page_header) where last_page_header is
# True (this is the last page), False (more pages), or None (header absent).
PageFetch = Callable[[int], Awaitable[tuple[list[Any], bool | None]]]


class PaginationError(Exception):
    pass


def _fingerprint(items: list[Any]) -> tuple[Any, ...]:
    def key(item: Any) -> Any:
        if isinstance(item, dict):
            return item.get("id", repr(item))
        return getattr(item, "id", repr(item))

    return tuple(key(item) for item in items)


async def collect_paged(
    fetch: PageFetch,
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    max_pages: int = MAX_PAGES,
) -> list[Any]:
    collected: list[Any] = []
    previous: tuple[Any, ...] | None = None
    for page in range(1, max_pages + 1):
        items, last_page = await fetch(page)
        if items:
            fingerprint = _fingerprint(items)
            if fingerprint == previous:
                raise PaginationError(
                    f"page {page} repeated the previous page; refusing a pagination loop"
                )
            previous = fingerprint
            collected.extend(items)
        if last_page is True or not items or len(items) < page_size:
            return collected
    raise PaginationError(
        f"pagination exceeded {max_pages} pages; refusing to return a partial list"
    )
