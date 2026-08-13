"""Permanent operation record types.

One frozen `Operation` constant exists per Clockify endpoint (168 total),
hand-authored from `docs/port/OPERATION_PORT_MANIFEST.md`. Every field has an
active runtime consumer; nothing here is documentation-only metadata.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class Service(StrEnum):
    REGULAR = "regular"
    REPORTS = "reports"
    AUDIT_LOG = "audit_log"


class RequestEncoding(StrEnum):
    NONE = "none"
    JSON = "json"
    MULTIPART = "multipart"


class ResponseKind(StrEnum):
    JSON = "json"
    BYTES = "bytes"
    TEXT = "text"
    NONE = "none"
    CONTENT_NEGOTIATED = "content_negotiated"


class MutationEffect(StrEnum):
    NONE = "none"
    CREATE = "create"
    REPLACE = "replace"
    PATCH = "patch"
    TRANSITION = "transition"
    DELETE = "delete"
    BULK = "bulk"


class ReplacementSemantics(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    PATCH = "patch"
    FULL_REPLACE_PROVEN = "full_replace_proven"
    MIXED_PROVEN = "mixed_proven"
    UNKNOWN_CONSERVATIVE = "unknown_conservative"


# `lifecycle` values form a small closed vocabulary:
#   archive_before_delete — entity must be archived before DELETE succeeds
#   done_before_delete    — task must be DONE before DELETE succeeds
#   pending_only          — operation is valid only while the entity is PENDING
LIFECYCLE_VALUES = frozenset({"archive_before_delete", "done_before_delete", "pending_only"})


@dataclass(frozen=True, slots=True)
class QueryParameter:
    python_name: str
    wire_name: str
    style: str = "form"
    explode: bool = True
    required: bool = False


@dataclass(frozen=True, slots=True)
class PaginationSpec:
    page_parameter: str
    page_size_parameter: str
    items_path: tuple[str, ...] | None
    count_path: tuple[str, ...] | None = None
    last_page_header: bool = False


@dataclass(frozen=True, slots=True)
class OperationSemantics:
    mutates: bool
    effect: MutationEffect
    replacement: ReplacementSemantics
    lifecycle: str | None = None
    replacement_required_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.lifecycle is not None and self.lifecycle not in LIFECYCLE_VALUES:
            raise ValueError(f"unknown lifecycle {self.lifecycle!r}")
        if self.mutates != (self.effect is not MutationEffect.NONE):
            raise ValueError("mutates flag must match effect")


@dataclass(frozen=True, slots=True)
class Operation:
    operation_id: str
    resource: str
    sdk_method: str
    http_method: str
    service: Service
    path: str
    path_parameters: tuple[str, ...]
    query_parameters: tuple[QueryParameter, ...] = ()
    request_encoding: RequestEncoding = RequestEncoding.NONE
    response_kind: ResponseKind = ResponseKind.JSON
    pagination: PaginationSpec | None = None
    semantics: OperationSemantics = field(
        default=OperationSemantics(
            mutates=False,
            effect=MutationEffect.NONE,
            replacement=ReplacementSemantics.NOT_APPLICABLE,
        )
    )
