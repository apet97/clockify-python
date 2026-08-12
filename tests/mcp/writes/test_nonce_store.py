# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportArgumentType=false, reportCallIssue=false, reportUnknownVariableType=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportMissingParameterType=false
"""Safety Phase B: bounded atomic nonce store."""

import asyncio

import pytest

from clockify_mcp.writes.canonical import canonical_json
from clockify_mcp.writes.nonce_store import (
    ConfirmationAlreadyUsed,
    ConfirmationExpired,
    ConfirmationMismatch,
    ConfirmationNotFound,
    InMemoryNonceStore,
    PlanTooLarge,
    StoreAtCapacity,
)
from clockify_mcp.writes.plan import WritePlan, WriteStep


def make_plan(name: str = "billing") -> WritePlan:
    return WritePlan(
        version=1,
        title="Create tag",
        summary=f"Create tag {name!r}",
        effect="create",
        scope="one entity",
        sensitivity=(),
        reversibility="reversible",
        steps=(
            WriteStep(
                operation_id="postWorkspacesWorkspaceIdTags",
                path_arguments=(("workspaceId", "w1"),),
                body_json=canonical_json({"name": name}),
            ),
        ),
    )


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def issue_kwargs(plan: WritePlan, key: str = "k1") -> dict:  # type: ignore[type-arg]
    return {
        "key": key,
        "principal_id": "principal-a",
        "tool_name": "clockify_tags_create",
        "workspace_id": "w1",
        "arguments_digest": "argdigest",
        "plan": plan,
    }


def consume_kwargs(prepared) -> dict:  # type: ignore[no-untyped-def, type-arg]
    return {
        "nonce": prepared.nonce,
        "principal_id": prepared.principal_id,
        "tool_name": prepared.tool_name,
        "workspace_id": prepared.workspace_id,
        "arguments_digest": prepared.arguments_digest,
        "plan_digest": prepared.plan_digest,
    }


async def test_same_key_same_plan_returns_same_nonce() -> None:
    store = InMemoryNonceStore()
    plan = make_plan()
    first = await store.get_or_issue(**issue_kwargs(plan))
    second = await store.get_or_issue(**issue_kwargs(plan))
    assert first.nonce == second.nonce  # stable across MRTR rounds


async def test_changed_plan_invalidates_old_nonce() -> None:
    store = InMemoryNonceStore()
    first = await store.get_or_issue(**issue_kwargs(make_plan("a")))
    second = await store.get_or_issue(**issue_kwargs(make_plan("b")))
    assert first.nonce != second.nonce
    with pytest.raises(ConfirmationNotFound):
        await store.consume(**consume_kwargs(first))


async def test_consume_once_then_tombstone() -> None:
    store = InMemoryNonceStore()
    prepared = await store.get_or_issue(**issue_kwargs(make_plan()))
    permit = await store.consume(**consume_kwargs(prepared))
    assert permit.plan is prepared.plan
    with pytest.raises(ConfirmationAlreadyUsed, match="confirmation_already_used"):
        await store.consume(**consume_kwargs(prepared))


async def test_hundred_concurrent_consumers_yield_one_permit() -> None:
    store = InMemoryNonceStore()
    prepared = await store.get_or_issue(**issue_kwargs(make_plan()))
    results = await asyncio.gather(
        *(store.consume(**consume_kwargs(prepared)) for _ in range(100)),
        return_exceptions=True,
    )
    permits = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]
    assert len(permits) == 1
    assert len(failures) == 99
    assert all(isinstance(f, ConfirmationAlreadyUsed) for f in failures)


async def test_exact_ttl_boundary() -> None:
    clock = Clock()
    store = InMemoryNonceStore(ttl=300.0, clock=clock)
    prepared = await store.get_or_issue(**issue_kwargs(make_plan()))
    clock.now += 300.0  # exactly at expiry: expired
    with pytest.raises((ConfirmationExpired, ConfirmationNotFound)):
        await store.consume(**consume_kwargs(prepared))


async def test_just_before_ttl_still_valid() -> None:
    clock = Clock()
    store = InMemoryNonceStore(ttl=300.0, clock=clock)
    prepared = await store.get_or_issue(**issue_kwargs(make_plan()))
    clock.now += 299.999
    permit = await store.consume(**consume_kwargs(prepared))
    assert permit.tool_name == "clockify_tags_create"


async def test_capacity_boundary_and_prune_first() -> None:
    clock = Clock()
    store = InMemoryNonceStore(max_pending=2, clock=clock)
    await store.get_or_issue(**issue_kwargs(make_plan("a"), key="k1"))
    await store.get_or_issue(**issue_kwargs(make_plan("b"), key="k2"))
    with pytest.raises(StoreAtCapacity):
        await store.get_or_issue(**issue_kwargs(make_plan("c"), key="k3"))
    # After expiry, pruning frees capacity before the check.
    clock.now += 301.0
    third = await store.get_or_issue(**issue_kwargs(make_plan("c"), key="k3"))
    assert third.nonce


async def test_plan_byte_boundary() -> None:
    store = InMemoryNonceStore(max_plan_bytes=64)
    big = make_plan("x" * 200)
    with pytest.raises(PlanTooLarge):
        await store.get_or_issue(**issue_kwargs(big))


async def test_cancel_removes_pending() -> None:
    store = InMemoryNonceStore()
    prepared = await store.get_or_issue(**issue_kwargs(make_plan()))
    await store.cancel(prepared.nonce)
    with pytest.raises(ConfirmationNotFound):
        await store.consume(**consume_kwargs(prepared))


@pytest.mark.parametrize(
    "field, value",
    [
        ("principal_id", "principal-b"),
        ("tool_name", "clockify_tags_delete"),
        ("arguments_digest", "otherdigest"),
        ("plan_digest", "00" * 32),
    ],
)
async def test_binding_mismatch_rejected(field: str, value: str) -> None:
    store = InMemoryNonceStore()
    prepared = await store.get_or_issue(**issue_kwargs(make_plan()))
    kwargs = consume_kwargs(prepared)
    kwargs[field] = value
    with pytest.raises(ConfirmationMismatch):
        await store.consume(**kwargs)
    # The record is still pending and the exact binding still works once.
    await store.consume(**consume_kwargs(prepared))


async def test_restart_loses_all_pending_state() -> None:
    store = InMemoryNonceStore()
    prepared = await store.get_or_issue(**issue_kwargs(make_plan()))
    fresh_store = InMemoryNonceStore()  # simulated process restart
    with pytest.raises(ConfirmationNotFound):
        await fresh_store.consume(**consume_kwargs(prepared))


async def test_replay_after_late_consume_reports_already_used() -> None:
    # A nonce consumed just before its own expiry must keep its tombstone for
    # a full ttl after consumption, so a prompt replay still says "already
    # used" rather than degrading to "not found".
    clock = Clock()
    store = InMemoryNonceStore(ttl=300.0, clock=clock)
    prepared = await store.get_or_issue(**issue_kwargs(make_plan()))
    clock.now += 299.0
    await store.consume(**consume_kwargs(prepared))
    clock.now += 2.0  # past the original expires_at, well within ttl of consume
    with pytest.raises(ConfirmationAlreadyUsed):
        await store.consume(**consume_kwargs(prepared))


async def test_tombstone_expires() -> None:
    clock = Clock()
    store = InMemoryNonceStore(ttl=300.0, clock=clock)
    prepared = await store.get_or_issue(**issue_kwargs(make_plan()))
    await store.consume(**consume_kwargs(prepared))
    clock.now += 301.0
    # After tombstone expiry the nonce is simply unknown, not "already used".
    with pytest.raises(ConfirmationNotFound):
        await store.consume(**consume_kwargs(prepared))
