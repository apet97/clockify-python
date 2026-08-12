"""The single runtime source of operation truth.

`ALL_OPERATIONS` is built from explicit imports and a tuple literal — no
decorators, scanning, or import-time side effects beyond plain module import.
Count assertions (168/62/106/49/13, hosts, multipart) live in tests, not here.
"""

from clockify.operations import (
    approvals,
    audit_log,
    clients,
    custom_fields,
    entity_changes,
    expense_categories,
    expenses,
    files,
    holidays,
    invoice_items,
    invoice_payments,
    invoice_settings,
    invoices,
    member_profiles,
    projects,
    reports,
    scheduling,
    shared_reports,
    tags,
    tasks,
    time_entries,
    time_off_balance_assignments,
    time_off_balances,
    time_off_policies,
    time_off_requests,
    user_groups,
    users,
    webhooks,
    workspaces,
)
from clockify.operations.model import Operation

ALL_OPERATIONS: tuple[Operation, ...] = (
    *approvals.OPERATIONS,
    *audit_log.OPERATIONS,
    *clients.OPERATIONS,
    *custom_fields.OPERATIONS,
    *entity_changes.OPERATIONS,
    *expense_categories.OPERATIONS,
    *expenses.OPERATIONS,
    *files.OPERATIONS,
    *holidays.OPERATIONS,
    *invoice_items.OPERATIONS,
    *invoice_payments.OPERATIONS,
    *invoice_settings.OPERATIONS,
    *invoices.OPERATIONS,
    *member_profiles.OPERATIONS,
    *projects.OPERATIONS,
    *reports.OPERATIONS,
    *scheduling.OPERATIONS,
    *shared_reports.OPERATIONS,
    *tags.OPERATIONS,
    *tasks.OPERATIONS,
    *time_entries.OPERATIONS,
    *time_off_balance_assignments.OPERATIONS,
    *time_off_balances.OPERATIONS,
    *time_off_policies.OPERATIONS,
    *time_off_requests.OPERATIONS,
    *user_groups.OPERATIONS,
    *users.OPERATIONS,
    *webhooks.OPERATIONS,
    *workspaces.OPERATIONS,
)


def _build_maps() -> tuple[dict[str, Operation], dict[tuple[str, str], Operation]]:
    by_id: dict[str, Operation] = {}
    by_public_method: dict[tuple[str, str], Operation] = {}
    for operation in ALL_OPERATIONS:
        if operation.operation_id in by_id:
            raise ValueError(f"duplicate operation_id {operation.operation_id!r}")
        by_id[operation.operation_id] = operation
        key = (operation.resource, operation.sdk_method)
        if key in by_public_method:
            raise ValueError(f"duplicate public method {key!r}")
        by_public_method[key] = operation
    return by_id, by_public_method


BY_ID, BY_PUBLIC_METHOD = _build_maps()
