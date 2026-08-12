# pyright: reportUnusedFunction=false
"""Explicit registration of all 60 raw read tools, grouped by domain.


No decorator scanning: each domain module's `register` is called by name here.
The count and read-only mapping are asserted in tests, not at import time.
"""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.tools import (
    approvals,
    audit_log,
    clients,
    custom_fields,
    entity_changes,
    expense_categories,
    expenses,
    holidays,
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


def register_read_tools(server: MCPServer, client: ClockifyClient) -> None:
    approvals.register(server, client)
    audit_log.register(server, client)
    clients.register(server, client)
    custom_fields.register(server, client)
    entity_changes.register(server, client)
    expense_categories.register(server, client)
    expenses.register(server, client)
    holidays.register(server, client)
    invoice_payments.register(server, client)
    invoice_settings.register(server, client)
    invoices.register(server, client)
    member_profiles.register(server, client)
    projects.register(server, client)
    reports.register(server, client)
    scheduling.register(server, client)
    shared_reports.register(server, client)
    tags.register(server, client)
    tasks.register(server, client)
    time_entries.register(server, client)
    time_off_balance_assignments.register(server, client)
    time_off_balances.register(server, client)
    time_off_policies.register(server, client)
    time_off_requests.register(server, client)
    user_groups.register(server, client)
    users.register(server, client)
    webhooks.register(server, client)
    workspaces.register(server, client)
