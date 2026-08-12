"""Regression guards for write-safety review findings A and (preview) headline.

Findings A (plan-size cap) and P (preview shows the bound body) are fixed;
these tests now guard the corrected behavior. See docs/mcp-write-safety-review.md.
"""

import json
from dataclasses import fields

import pytest

from clockify_mcp.writes.canonical import canonical_json
from clockify_mcp.writes.nonce_store import InMemoryNonceStore, PlanTooLarge
from clockify_mcp.writes.plan import (
    FileDigest,
    Precondition,
    PreparedWrite,
    PreviewField,
    ReconciliationPlan,
    WritePlan,
    WriteStep,
    render_preview,
    retained_plan_bytes,
)


def _step() -> WriteStep:
    return WriteStep(
        operation_id="postWorkspacesWorkspaceIdTags",
        path_arguments=(("workspaceId", "w1"),),
        body_json=canonical_json({"name": "x"}),
    )


def _plan(**over) -> WritePlan:  # type: ignore[no-untyped-def]
    kw = {
        "version": 1,
        "title": "t",
        "summary": "s",
        "effect": "create",
        "scope": "one",
        "sensitivity": (),
        "reversibility": "reversible",
        "steps": (_step(),),
    }
    kw.update(over)
    return WritePlan(**kw)  # type: ignore[arg-type]


async def test_huge_warnings_should_hit_byte_cap() -> None:
    store = InMemoryNonceStore(max_plan_bytes=4096)
    with pytest.raises(PlanTooLarge):
        await store.get_or_issue(
            key="k1",
            principal_id="p",
            tool_name="clockify_tags_create",
            workspace_id="w1",
            arguments_digest="a",
            plan=_plan(warnings=("W" * (1024 * 1024),)),
        )


async def test_multibyte_and_reconciliation_content_hit_byte_cap() -> None:
    plan = _plan(
        title="😀",
        summary="😀",
        effect="😀",
        scope="😀",
        sensitivity=("😀",),
        reversibility="😀",
        steps=(
            WriteStep(
                operation_id="postWorkspacesWorkspaceIdTags",
                path_arguments=(("😀", "😀"),),
                query=(("😀", "😀"),),
                body_json=canonical_json({"value": "😀"}),
                multipart_fields=(("😀", "😀"),),
                files=(FileDigest("😀", "😀", 4, "😀", "a" * 64),),
            ),
        ),
        preconditions=(Precondition("😀", "😀"),),
        preview_fields=(PreviewField("😀", "😀"),),
        warnings=("😀",),
        reconciliation=ReconciliationPlan(
            kind="direct_get",
            description="😀" * 100,
            operation_id="getWorkspacesWorkspaceIdTagsTagId",
            path_arguments=(("😀", "😀"),),
        ),
    )
    encoded = retained_plan_bytes(plan)
    assert "😀".encode() in encoded
    store = InMemoryNonceStore(max_plan_bytes=len(encoded) - 1)
    with pytest.raises(PlanTooLarge):
        await store.get_or_issue(
            key="unicode",
            principal_id="p",
            tool_name="clockify_tags_create",
            workspace_id="w1",
            arguments_digest="a",
            plan=plan,
        )


async def test_retained_plan_exact_byte_boundary() -> None:
    plan = _plan(reconciliation=ReconciliationPlan("none", "bounded"))
    size = len(retained_plan_bytes(plan))
    exact = InMemoryNonceStore(max_plan_bytes=size)
    await exact.get_or_issue(
        key="exact",
        principal_id="p",
        tool_name="clockify_tags_create",
        workspace_id="w1",
        arguments_digest="a",
        plan=plan,
    )
    over = InMemoryNonceStore(max_plan_bytes=size - 1)
    with pytest.raises(PlanTooLarge):
        await over.get_or_issue(
            key="over",
            principal_id="p",
            tool_name="clockify_tags_create",
            workspace_id="w1",
            arguments_digest="a",
            plan=plan,
        )


def test_retained_representation_covers_every_dataclass_field() -> None:
    plan = _plan(reconciliation=ReconciliationPlan("none", "covered"))
    retained = json.loads(retained_plan_bytes(plan))
    assert set(retained) == {field.name for field in fields(WritePlan)}
    assert set(retained["steps"][0]) == {field.name for field in fields(WriteStep)}
    assert set(retained["reconciliation"]) == {field.name for field in fields(ReconciliationPlan)}


def test_preview_should_show_bound_body() -> None:
    step = WriteStep(
        operation_id="postWorkspacesWorkspaceIdTags",
        path_arguments=(("workspaceId", "w1"),),
        body_json=canonical_json({"name": "evil", "archived": True}),
    )
    plan = _plan(
        steps=(step,), summary="harmless", preview_fields=(PreviewField("Name", "harmless"),)
    )
    prepared = PreparedWrite(
        key="k",
        nonce="n" * 40,
        principal_id="p",
        tool_name="clockify_tags_create",
        workspace_id=None,
        arguments_digest="a",
        plan=plan,
        plan_digest=plan.digest,
        issued_at=0.0,
        expires_at=60.0,
    )
    text = render_preview(prepared)
    # The human must be shown what actually dispatches.
    assert "evil" in text
    assert "archived" in text
