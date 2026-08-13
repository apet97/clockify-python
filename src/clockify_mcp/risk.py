"""Risk classification for every registered tool.

The tier decides behavior once, in one place:

- ``READ`` — dispatches through ``ReadOnlyExecutor``.
- ``ROUTINE_WRITE`` — executes directly, single attempt, no approval round trip.
- The four guarded tiers — every call passes the sealed write gate
  (deterministic preview, model-invisible approval, atomic nonce, byte-exact
  dispatch).

``RISK_BY_TOOL`` must cover the full server's registered tool set exactly;
``tests/mcp/test_full_surface.py`` enforces the equality, so an unclassified
tool is a test failure, never a silent default.
"""

from enum import StrEnum

from mcp.types import ToolAnnotations


class Risk(StrEnum):
    READ = "read"
    ROUTINE_WRITE = "routine_write"
    BUSINESS_WRITE = "business_write"
    EXTERNAL_SIDE_EFFECT = "external_side_effect"
    PRIVILEGED = "privileged"
    DESTRUCTIVE = "destructive"


GUARDED_RISKS = frozenset(
    {Risk.BUSINESS_WRITE, Risk.EXTERNAL_SIDE_EFFECT, Risk.PRIVILEGED, Risk.DESTRUCTIVE}
)


def annotations_for(risk: Risk) -> ToolAnnotations:
    """Advisory MCP hints derived from the tier. Hints are never the boundary."""
    if risk is Risk.READ:
        return ToolAnnotations(
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=True,
        )
    return ToolAnnotations(
        read_only_hint=False,
        destructive_hint=risk is Risk.DESTRUCTIVE,
        idempotent_hint=False,
        open_world_hint=True,
    )


# Every registered tool, by name. Reads and read workflows are all READ;
# write tools and write workflows are appended by their registering modules'
# domain constants below as waves land.
_READ_TOOLS = (
    "clockify_approvals_list",
    "clockify_audit_log_search",
    "clockify_clients_get",
    "clockify_clients_list",
    "clockify_custom_fields_list_for_project",
    "clockify_custom_fields_list_for_workspace",
    "clockify_entity_changes_list_created",
    "clockify_entity_changes_list_deleted",
    "clockify_entity_changes_list_updated",
    "clockify_expense_categories_list",
    "clockify_expenses_get",
    "clockify_expenses_list",
    "clockify_holidays_list",
    "clockify_holidays_list_in_period",
    "clockify_invoice_payments_list",
    "clockify_invoice_settings_get",
    "clockify_invoices_filter",
    "clockify_invoices_get",
    "clockify_invoices_list",
    "clockify_member_profiles_get",
    "clockify_projects_get",
    "clockify_projects_list",
    "clockify_reports_attendance",
    "clockify_reports_detailed",
    "clockify_reports_expense_details",
    "clockify_reports_summary",
    "clockify_reports_weekly",
    "clockify_scheduling_get_filtered_user_capacity",
    "clockify_scheduling_get_project_totals",
    "clockify_scheduling_get_user_capacity",
    "clockify_scheduling_list_assignments",
    "clockify_scheduling_list_project_totals",
    "clockify_shared_reports_list",
    "clockify_shared_reports_view_public",
    "clockify_tags_get",
    "clockify_tags_list",
    "clockify_tasks_get",
    "clockify_tasks_list",
    "clockify_time_entries_get",
    "clockify_time_entries_get_many",
    "clockify_time_entries_list_for_user",
    "clockify_time_entries_list_in_progress",
    "clockify_time_off_balance_assignments_get_for_user_and_policy",
    "clockify_time_off_balances_list_for_policy",
    "clockify_time_off_balances_list_for_user",
    "clockify_time_off_policies_get",
    "clockify_time_off_policies_list",
    "clockify_time_off_requests_list",
    "clockify_user_groups_list",
    "clockify_users_filter",
    "clockify_users_list",
    "clockify_users_list_managers",
    "clockify_users_me",
    "clockify_webhooks_get",
    "clockify_webhooks_list",
    "clockify_webhooks_list_event_statuses",
    "clockify_webhooks_list_for_addon",
    "clockify_webhooks_search_logs",
    "clockify_workspaces_get",
    "clockify_workspaces_list",
)

_READ_WORKFLOWS = (
    "clockify_status",
    "clockify_workspace_overview",
    "clockify_review_day",
    "clockify_review_week",
    "clockify_doctor",
)

_WRITE_TOOLS: dict[str, Risk] = {
    "clockify_tags_create": Risk.BUSINESS_WRITE,
}

RISK_BY_TOOL: dict[str, Risk] = {
    **dict.fromkeys(_READ_TOOLS + _READ_WORKFLOWS, Risk.READ),
    **_WRITE_TOOLS,
}
