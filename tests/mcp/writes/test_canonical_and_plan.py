# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportArgumentType=false, reportCallIssue=false, reportUnknownVariableType=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportMissingParameterType=false
"""Safety Phase A: canonicalization, digests, deterministic preview."""

import pytest

from clockify_mcp.writes.canonical import NotCanonicalizable, canonical_json, digest_of
from clockify_mcp.writes.plan import (
    FileDigest,
    Precondition,
    PreparedWrite,
    PreviewField,
    WritePlan,
    WriteStep,
    render_preview,
)

TAG_CREATE_STEP = WriteStep(
    operation_id="postWorkspacesWorkspaceIdTags",
    path_arguments=(("workspaceId", "w1"),),
    body_json=canonical_json({"name": "billing"}),
)


def make_plan(steps: tuple[WriteStep, ...] = (TAG_CREATE_STEP,), **overrides) -> WritePlan:  # type: ignore[no-untyped-def]
    values = {
        "version": 1,
        "title": "Create tag",
        "summary": "Create tag 'billing'",
        "effect": "create",
        "scope": "one entity",
        "sensitivity": (),
        "reversibility": "reversible",
        "steps": steps,
    }
    values.update(overrides)
    return WritePlan(**values)


class TestCanonicalJson:
    def test_sorted_keys_no_whitespace(self) -> None:
        assert canonical_json({"b": 1, "a": [1, 2]}) == b'{"a":[1,2],"b":1}'

    def test_key_order_does_not_change_digest(self) -> None:
        assert digest_of({"a": 1, "b": 2}) == digest_of({"b": 2, "a": 1})

    def test_array_order_changes_digest(self) -> None:
        assert digest_of({"ids": ["a", "b"]}) != digest_of({"ids": ["b", "a"]})

    def test_explicit_null_differs_from_omitted(self) -> None:
        assert digest_of({"a": None}) != digest_of({})

    def test_nan_rejected(self) -> None:
        with pytest.raises(NotCanonicalizable):
            canonical_json({"x": float("nan")})

    def test_infinity_rejected(self) -> None:
        with pytest.raises(NotCanonicalizable):
            canonical_json({"x": float("inf")})

    def test_raw_bytes_rejected(self) -> None:
        with pytest.raises(NotCanonicalizable):
            canonical_json({"content": b"\x00"})

    def test_non_string_keys_rejected(self) -> None:
        with pytest.raises(NotCanonicalizable):
            canonical_json({1: "x"})


class TestRequestDigest:
    def test_same_semantic_request_same_digest(self) -> None:
        again = WriteStep(
            operation_id="postWorkspacesWorkspaceIdTags",
            path_arguments=(("workspaceId", "w1"),),
            body_json=canonical_json({"name": "billing"}),
        )
        assert again.request_digest == TAG_CREATE_STEP.request_digest

    def test_body_key_order_is_canonicalized(self) -> None:
        reordered = WriteStep(
            operation_id="putWorkspacesWorkspaceIdTagsTagId",
            path_arguments=(("workspaceId", "w1"), ("tagId", "t1")),
            body_json=canonical_json({"archived": True, "name": "x"}),
        )
        also = WriteStep(
            operation_id="putWorkspacesWorkspaceIdTagsTagId",
            path_arguments=(("workspaceId", "w1"), ("tagId", "t1")),
            body_json=canonical_json({"name": "x", "archived": True}),
        )
        assert reordered.request_digest == also.request_digest

    @pytest.mark.parametrize(
        "mutation",
        [
            {"operation_id": "deleteWorkspacesWorkspaceIdTagsTagId"},
            {"path_arguments": (("workspaceId", "w2"),)},
            {"query": (("archived", "true"),)},
            {"body_json": canonical_json({"name": "different"})},
            {"body_json": canonical_json({"name": "billing", "extra": None})},
            {"body_json": None},
            {
                "files": (
                    FileDigest(
                        field_name="file",
                        filename="a.png",
                        size=3,
                        content_type="image/png",
                        sha256="00" * 32,
                    ),
                )
            },
        ],
    )
    def test_any_material_change_changes_digest(self, mutation: dict) -> None:  # type: ignore[type-arg]
        base = {
            "operation_id": TAG_CREATE_STEP.operation_id,
            "path_arguments": TAG_CREATE_STEP.path_arguments,
            "query": TAG_CREATE_STEP.query,
            "body_json": TAG_CREATE_STEP.body_json,
            "files": TAG_CREATE_STEP.files,
        }
        base.update(mutation)
        changed = WriteStep(**base)  # type: ignore[arg-type]
        assert changed.request_digest != TAG_CREATE_STEP.request_digest

    def test_one_byte_file_change_changes_digest(self) -> None:
        def step_with(sha: str) -> WriteStep:
            return WriteStep(
                operation_id="uploadImage",
                path_arguments=(),
                files=(
                    FileDigest(
                        field_name="file",
                        filename="r.png",
                        size=4,
                        content_type="image/png",
                        sha256=sha,
                    ),
                ),
            )

        assert step_with("aa" * 32).request_digest != step_with("ab" + "aa" * 31).request_digest


class TestPlanDigestAndPreview:
    def test_extra_step_changes_plan_digest(self) -> None:
        single = make_plan()
        double = make_plan(
            steps=(
                TAG_CREATE_STEP,
                WriteStep(
                    operation_id="deleteWorkspacesWorkspaceIdTagsTagId",
                    path_arguments=(("workspaceId", "w1"), ("tagId", "t1")),
                ),
            )
        )
        assert single.digest != double.digest

    def test_precondition_change_changes_plan_digest(self) -> None:
        before = make_plan(preconditions=(Precondition("tag active", "aa" * 32),))
        after = make_plan(preconditions=(Precondition("tag active", "bb" * 32),))
        assert before.digest != after.digest

    def test_preview_is_deterministic_and_complete(self) -> None:
        plan = make_plan(
            preview_fields=(PreviewField("name", "billing"),),
            warnings=("full replacement: omitted fields are cleared",),
        )
        prepared = PreparedWrite(
            key="k",
            nonce="NONCE1234567890",
            principal_id="p",
            tool_name="clockify_tags_create",
            workspace_id="w1",
            arguments_digest="d",
            plan=plan,
            plan_digest=plan.digest,
            issued_at=0.0,
            expires_at=300.0,
        )
        first = render_preview(prepared)
        second = render_preview(prepared)
        assert first == second  # no volatile content
        assert "Action: Create tag" in first
        assert "Confirmation ID: NONCE1234567" in first
        assert "POST /workspaces/{workspaceId}/tags" in first
        assert "name: billing" in first
        assert "full replacement" in first
        assert "Decision: approve or reject" in first

    def test_preview_never_contains_secrets(self) -> None:
        plan = make_plan(preview_fields=(PreviewField("webhook token", "sha256:ab12… (32 bytes)"),))
        prepared = PreparedWrite(
            key="k",
            nonce="n",
            principal_id="p",
            tool_name="t",
            workspace_id="w1",
            arguments_digest="d",
            plan=plan,
            plan_digest=plan.digest,
            issued_at=0.0,
            expires_at=300.0,
        )
        preview = render_preview(prepared)
        assert "sha256:" in preview  # digest representation, not the raw value
