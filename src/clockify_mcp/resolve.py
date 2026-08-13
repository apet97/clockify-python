"""Name-to-id resolution for workflows.

A 24-hex value is treated as an id and returned unchanged. Anything else is
matched case-insensitively against the full paged list (archived included) —
one exact match resolves, several raise ``AmbiguousNameError`` (which
workflows turn into a clarification receipt with real candidates), none raises
an actionable error. Resolution never guesses.
"""

import re
from collections.abc import Awaitable, Callable
from typing import Any

from clockify_mcp.errors import ToolError
from clockify_mcp.paging import collect_paged
from clockify_mcp.receipt import EntityRef

_ID_PATTERN = re.compile(r"^[0-9a-f]{24}$")

# fetch(page) -> (items, last_page_header); items expose .id and the name keys.
ListFetch = Callable[[int], Awaitable[tuple[list[Any], bool | None]]]


class AmbiguousNameError(Exception):
    def __init__(self, label: str, value: str, candidates: list[EntityRef]) -> None:
        super().__init__(f"several {label}s are named {value!r}; pass an exact id")
        self.label = label
        self.value = value
        self.candidates = candidates


def _field(item: Any, key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


async def resolve_by_name(
    value: str,
    *,
    label: str,
    fetch: ListFetch,
    keys: tuple[str, ...] = ("name",),
) -> str:
    """Return the entity id for `value` (an id or an exact, unique name)."""
    if _ID_PATTERN.fullmatch(value):
        return value
    wanted = value.casefold()
    items = await collect_paged(fetch)
    matches = [
        item
        for item in items
        if any(
            isinstance(candidate := _field(item, key), str) and candidate.casefold() == wanted
            for key in keys
        )
    ]
    if len(matches) == 1:
        entity_id = _field(matches[0], "id")
        if isinstance(entity_id, str) and entity_id:
            return entity_id
        raise ToolError(f"matched {label} {value!r} has no id")
    if matches:
        candidates = [
            EntityRef(
                type=label,
                id=str(_field(item, "id") or ""),
                name=_field(item, keys[0]),
            )
            for item in matches
        ]
        raise AmbiguousNameError(label, value, candidates)
    raise ToolError(
        f"no {label} named {value!r} (not found); pass a 24-character id or an exact name"
    )
