"""Regression guards for write-safety review findings A and (preview) headline.

Findings A (plan-size cap) and P (preview shows the bound body) are fixed;
these tests now guard the corrected behavior. See docs/mcp-write-safety-review.md.
"""

import pytest

from clockify_mcp.writes.canonical import canonical_json
from clockify_mcp.writes.nonce_store import InMemoryNonceStore, PlanTooLarge
from clockify_mcp.writes.plan import (
    PreparedWrite,
    PreviewField,
    WritePlan,
    WriteStep,
    render_preview,
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
