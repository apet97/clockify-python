"""Operation-specific read-back after a dispatched write.

Reconciliation reads use the restricted read-only client. A failed read-back
turns a success into `succeeded_unreconciled` — never into a retry.
"""

from typing import Any

from clockify.client import ClockifyClient
from clockify.errors import ClockifyError
from clockify_mcp.writes.plan import ReconciliationPlan


async def reconcile(client: ClockifyClient, plan: ReconciliationPlan) -> tuple[bool, Any]:
    """Returns (reconciled, data). `reconciled=False` carries no failure semantics."""
    if plan.kind == "none":
        return False, None
    if plan.kind == "direct_get":
        assert plan.operation_id is not None
        try:
            response = await client.raw.call(plan.operation_id, path=dict(plan.path_arguments))
        except ClockifyError:
            return False, None
        return True, response.data
    if plan.kind == "list_diff":
        # The caller supplies before-state; generic list-diff runs in the write
        # tool where the before snapshot exists. Here we only re-list.
        assert plan.operation_id is not None
        try:
            response = await client.raw.call(plan.operation_id, path=dict(plan.path_arguments))
        except ClockifyError:
            return False, None
        return True, response.data
    raise ValueError(f"unknown reconciliation kind {plan.kind!r}")
