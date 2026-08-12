"""Review finding F2: workspace binding of pending confirmations.

Otherwise identical requests in workspace A and workspace B must never share
or consume one confirmation. Covered at all three layers: key derivation,
stored-record lookup on reuse, and consume-time verification.
"""

import dataclasses

import pytest

from clockify._transport.auth import Credential
from clockify_mcp.writes.canonical import canonical_json
from clockify_mcp.writes.gate import WriteGate
from clockify_mcp.writes.nonce_store import ConfirmationMismatch
from clockify_mcp.writes.plan import WritePlan, WriteStep
from clockify_mcp.writes.principal import derive_key, new_process_secret


def _plan(workspace_id: str) -> WritePlan:
    return WritePlan(
        version=1,
        title="Create tag",
        summary="Create tag 'x'",
        effect="create",
        scope="one entity",
        sensitivity=(),
        reversibility="reversible",
        steps=(
            WriteStep(
                operation_id="postWorkspacesWorkspaceIdTags",
                path_arguments=(("workspaceId", workspace_id),),
                body_json=canonical_json({"name": "x"}),
            ),
        ),
    )


def _gate() -> WriteGate:
    return WriteGate(
        process_secret=new_process_secret(),
        credential=Credential(api_key="sacrificial-key"),
    )


def test_derive_key_differs_by_workspace_only() -> None:
    secret = new_process_secret()
    common = (secret, "principal-1", "clockify_tags_create", "digest-1")
    key_a = derive_key(*common, "workspace-a")
    key_b = derive_key(*common, "workspace-b")
    key_none = derive_key(*common, None)
    assert len({key_a, key_b, key_none}) == 3
    # Same workspace stays stable across rounds.
    assert key_a == derive_key(*common, "workspace-a")


async def test_prepare_in_two_workspaces_yields_distinct_pending_records() -> None:
    gate = _gate()
    arguments = {"name": "x"}
    prepared_a = await gate.prepare(
        tool_name="clockify_tags_create",
        arguments=arguments,
        workspace_id="workspace-a",
        plan=_plan("workspace-a"),
    )
    prepared_b = await gate.prepare(
        tool_name="clockify_tags_create",
        arguments=arguments,
        workspace_id="workspace-b",
        plan=_plan("workspace-b"),
    )
    assert prepared_a.key != prepared_b.key
    assert prepared_a.nonce != prepared_b.nonce
    # Each confirmation consumes only itself; both stay independently valid.
    permit_a = await gate.consume(prepared_a)
    permit_b = await gate.consume(prepared_b)
    assert permit_a.permit_id != permit_b.permit_id


async def test_prepare_same_workspace_same_plan_reuses_one_record() -> None:
    gate = _gate()
    first = await gate.prepare(
        tool_name="clockify_tags_create",
        arguments={"name": "x"},
        workspace_id="workspace-a",
        plan=_plan("workspace-a"),
    )
    second = await gate.prepare(
        tool_name="clockify_tags_create",
        arguments={"name": "x"},
        workspace_id="workspace-a",
        plan=_plan("workspace-a"),
    )
    assert first.nonce == second.nonce


async def test_consume_verifies_workspace_against_stored_record() -> None:
    gate = _gate()
    prepared = await gate.prepare(
        tool_name="clockify_tags_create",
        arguments={"name": "x"},
        workspace_id="workspace-a",
        plan=_plan("workspace-a"),
    )
    tampered = dataclasses.replace(prepared, workspace_id="workspace-b")
    with pytest.raises(ConfirmationMismatch):
        await gate.consume(tampered)
    # The honest confirmation is still single-use consumable afterwards.
    permit = await gate.consume(prepared)
    assert permit.tool_name == "clockify_tags_create"
