"""Response containers returned by the executor and raw escape hatch."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generic, TypeVar

import httpx

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ClockifyResponse(Generic[T]):
    """Decoded payload plus the transport metadata callers need for diagnosis."""

    data: T = field(repr=False)
    status_code: int
    headers: httpx.Headers = field(repr=False)
    request_id: str | None
    operation_id: str

    @property
    def last_page(self) -> bool | None:
        """Parsed `Last-Page` header; None when Clockify did not send it."""
        raw = self.headers.get("Last-Page")
        if raw is None:
            return None
        lowered = raw.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        return None


@dataclass(frozen=True, slots=True)
class BinaryResponse:
    """A binary download (receipt, invoice export). Bytes are exact, never text."""

    content: bytes
    content_type: str
    filename: str | None
    status_code: int
    headers: httpx.Headers
    request_id: str | None

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.write_bytes(self.content)
        return target


@dataclass(frozen=True, slots=True)
class TextResponse:
    """A decoded text/CSV payload."""

    text: str
    content_type: str
    status_code: int
    headers: httpx.Headers
    request_id: str | None


NegotiatedPayload = Any  # dict/list JSON, TextResponse, or BinaryResponse by content type
