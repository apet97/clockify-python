"""Write tool registration, one module per domain.

Mirrors ``clockify_mcp.tools``: every domain module defines
``register(server, deps)`` and is imported explicitly by name here.
``tests/mcp/test_full_surface.py`` asserts the resulting tool set, so a
missing or extra registration is a test failure.
"""

from mcp.server import MCPServer

from clockify_mcp.writes.runner import WriteDeps
from clockify_mcp.writes.tools import (
    approvals,
    clients,
    custom_fields,
    expense_categories,
    expenses,
    holidays,
    invoice_items,
    invoice_payments,
    invoice_settings,
    invoices,
    member_profiles,
    projects,
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

_DOMAIN_MODULES = (
    approvals,
    clients,
    custom_fields,
    expense_categories,
    expenses,
    holidays,
    invoice_items,
    invoice_payments,
    invoice_settings,
    invoices,
    member_profiles,
    projects,
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


def register_write_tools(server: MCPServer, deps: WriteDeps) -> None:
    for module in _DOMAIN_MODULES:
        module.register(server, deps)
