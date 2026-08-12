"""Canonical JSON: one encoder for arguments, wire bodies, plan hashes.

Deterministic across platforms: sorted keys, no whitespace, UTF-8, explicit
null preserved, non-finite floats rejected. Bytes never enter canonical JSON;
files are represented by digest metadata only.
"""

import hashlib
import json
import math
from typing import Any


class NotCanonicalizable(ValueError):
    pass


def _check(value: Any, path: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise NotCanonicalizable(f"{path}: non-finite float is not canonicalizable")
    if isinstance(value, bytes):
        raise NotCanonicalizable(f"{path}: raw bytes may only appear as FileDigest metadata")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise NotCanonicalizable(f"{path}: non-string object key {key!r}")
            _check(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _check(item, f"{path}[{index}]")
    elif value is not None and not isinstance(value, (str, int, float, bool)):
        raise NotCanonicalizable(f"{path}: unsupported type {type(value).__name__}")


def canonical_json(value: Any) -> bytes:
    """Sorted-key, no-whitespace, UTF-8 JSON. Raises on non-canonicalizable input."""
    _check(value, "$")
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_of(value: Any) -> str:
    return sha256_hex(canonical_json(value))
