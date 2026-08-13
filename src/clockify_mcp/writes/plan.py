"""Immutable write plans, exact wire binding, and the deterministic preview."""

import base64
from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from clockify.operations.model import Operation
from clockify.operations.registry import BY_ID
from clockify_mcp.writes.canonical import canonical_json, digest_of, sha256_hex


@dataclass(frozen=True, slots=True)
class FileDigest:
    field_name: str
    filename: str
    size: int
    content_type: str
    sha256: str


@dataclass(frozen=True, slots=True)
class Precondition:
    """Canonical fingerprint of the minimum relevant current-state fields."""

    description: str
    fingerprint: str  # digest_of(relevant fields); "" when no read route exists


@dataclass(frozen=True, slots=True)
class PreviewField:
    label: str
    value: str


@dataclass(frozen=True, slots=True)
class WriteStep:
    operation_id: str
    path_arguments: tuple[tuple[str, str], ...]
    query: tuple[tuple[str, str], ...] = ()
    body_json: bytes | None = None
    multipart_fields: tuple[tuple[str, str], ...] = ()
    files: tuple[FileDigest, ...] = ()

    @property
    def operation(self) -> Operation:
        return BY_ID[self.operation_id]

    @property
    def request_digest(self) -> str:
        """Covers destination semantics, not transport metadata (auth, request id)."""
        operation = self.operation
        material = {
            "operation_id": self.operation_id,
            "method": operation.http_method,
            "service": operation.service.value,
            "path_template": operation.path,
            "path_arguments": [list(pair) for pair in self.path_arguments],
            "query": [list(pair) for pair in self.query],
            "body_sha256": sha256_hex(self.body_json) if self.body_json is not None else None,
            "multipart_fields": [list(pair) for pair in self.multipart_fields],
            "files": [
                [f.field_name, f.filename, f.size, f.content_type, f.sha256] for f in self.files
            ],
        }
        return digest_of(material)


@dataclass(frozen=True, slots=True)
class ReconciliationPlan:
    kind: str  # "direct_get" | "list_diff" | "none"
    description: str
    operation_id: str | None = None
    path_arguments: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class WritePlan:
    version: int
    title: str
    summary: str
    effect: str
    scope: str
    sensitivity: tuple[str, ...]
    reversibility: str
    steps: tuple[WriteStep, ...]
    preconditions: tuple[Precondition, ...] = ()
    preview_fields: tuple[PreviewField, ...] = ()
    warnings: tuple[str, ...] = ()
    reconciliation: ReconciliationPlan | None = None

    @property
    def digest(self) -> str:
        # `reconciliation` is deliberately outside the digest: it is read-only,
        # runs post-dispatch, and executes from the permit's stored plan object,
        # never from re-supplied input (review finding D). If reconciliation ever
        # gains security-relevant behavior, add it here.
        material = {
            "version": self.version,
            "title": self.title,
            "summary": self.summary,
            "effect": self.effect,
            "scope": self.scope,
            "sensitivity": list(self.sensitivity),
            "reversibility": self.reversibility,
            "steps": [step.request_digest for step in self.steps],
            "preconditions": [[p.description, p.fingerprint] for p in self.preconditions],
            "preview_fields": [[f.label, f.value] for f in self.preview_fields],
            "warnings": list(self.warnings),
        }
        return digest_of(material)


def _retained_value(value: Any) -> Any:
    """Convert retained plan data to one canonical, future-field-safe shape."""
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _retained_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, bytes):
        return {"$bytes_base64": base64.b64encode(value).decode("ascii")}
    if isinstance(value, tuple):
        return [_retained_value(item) for item in value]
    return value


def retained_plan_bytes(plan: WritePlan) -> bytes:
    """Canonical UTF-8 representation of every dataclass field retained by a plan."""
    return canonical_json(_retained_value(plan))


@dataclass(frozen=True, slots=True)
class PreparedWrite:
    key: str
    nonce: str
    principal_id: str
    tool_name: str
    workspace_id: str | None
    arguments_digest: str
    plan: WritePlan
    plan_digest: str
    issued_at: float
    expires_at: float


def arguments_digest_of(arguments: dict[str, Any]) -> str:
    """Digest of validated model-visible arguments; omitted != explicit null."""
    return digest_of(arguments)


def render_preview(prepared: PreparedWrite) -> str:
    """Deterministic human preview. Contains nothing volatile beyond the stored nonce.

    Review finding P: the preview must show the exact bound wire data, not a
    builder-written summary alone. Every step's path arguments, query pairs, and
    canonical body are rendered from the same values the digest binds. Builders
    must never place raw secrets in bound bodies (W-13) — secret-bearing fields
    are digest-represented before plan construction.
    """
    plan = prepared.plan
    validity_seconds = int(prepared.expires_at - prepared.issued_at)
    lines = [
        f"Action: {plan.title}",
        f"Confirmation ID: {prepared.nonce[:12]}",
        f"Workspace: {prepared.workspace_id or '(user default)'}",
        f"Summary: {plan.summary}",
        f"Effect: {plan.effect}",
        f"Scope: {plan.scope}",
        f"Reversibility: {plan.reversibility}",
        "Steps (exact approved requests):",
    ]
    for index, step in enumerate(plan.steps, start=1):
        operation = step.operation
        lines.append(f"  {index}. {operation.http_method} {operation.path} ({step.operation_id})")
        for name, value in step.path_arguments:
            lines.append(f"     path {name}: {value}")
        for name, value in step.query:
            lines.append(f"     query {name}: {value}")
        if step.body_json is not None:
            lines.append(f"     body: {step.body_json.decode('utf-8')}")
        for name, value in step.multipart_fields:
            lines.append(f"     field {name}: {value}")
        for file_digest in step.files:
            lines.append(
                f"     file {file_digest.field_name}: {file_digest.filename} "
                f"({file_digest.size} bytes, {file_digest.content_type}, "
                f"sha256 {file_digest.sha256[:16]}…)"
            )
    if plan.preview_fields:
        lines.append("Details:")
        for preview_field in plan.preview_fields:
            lines.append(f"  {preview_field.label}: {preview_field.value}")
    for precondition in plan.preconditions:
        lines.append(f"Current state: {precondition.description}")
    if plan.warnings:
        lines.append("Warnings:")
        for warning in plan.warnings:
            lines.append(f"  - {warning}")
    lines.append(f"Valid for: {validity_seconds} seconds")
    lines.append("Decision: approve or reject")
    return "\n".join(lines)
