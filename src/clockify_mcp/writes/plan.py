"""Immutable write plans, exact wire binding, and the deterministic preview."""

from dataclasses import dataclass
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
    """Deterministic human preview. Contains nothing volatile beyond the stored nonce."""
    plan = prepared.plan
    lines = [
        f"Action: {plan.title}",
        f"Confirmation ID: {prepared.nonce[:12]}",
        f"Workspace: {prepared.workspace_id or '(user default)'}",
        f"Summary: {plan.summary}",
        f"Effect: {plan.effect}",
        f"Scope: {plan.scope}",
        f"Reversibility: {plan.reversibility}",
        "Steps:",
    ]
    for index, step in enumerate(plan.steps, start=1):
        operation = step.operation
        lines.append(f"  {index}. {operation.http_method} {operation.path} ({step.operation_id})")
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
    lines.append("Valid for: 5 minutes")
    lines.append("Decision: approve or reject")
    return "\n".join(lines)


def canonical_body(body: dict[str, Any] | list[Any] | None) -> bytes | None:
    return canonical_json(body) if body is not None else None
