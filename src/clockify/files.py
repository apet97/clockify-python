"""Multipart upload input for the three proven multipart endpoints."""

from dataclasses import dataclass
from typing import BinaryIO


@dataclass(slots=True)
class Upload:
    """A file to send. The SDK never closes a caller-owned file object."""

    filename: str
    content: "bytes | BinaryIO"
    content_type: str = "application/octet-stream"
