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
    # Orientation tools (full server only; static, no network).
    "clockify_tools_guide",
    "clockify_plan_change",
    "clockify_operation_guide",
    "clockify_sdk_snippet",
)

_WRITE_TOOLS: dict[str, Risk] = {
    # Write workflows.
    "clockify_start_work": Risk.ROUTINE_WRITE,
    "clockify_stop_work": Risk.ROUTINE_WRITE,
    "clockify_switch_work": Risk.ROUTINE_WRITE,
    "clockify_log_work": Risk.ROUTINE_WRITE,
    "clockify_fix_entry": Risk.ROUTINE_WRITE,
    "clockify_create_work_package": Risk.ROUTINE_WRITE,
    "clockify_demo_seed": Risk.ROUTINE_WRITE,
    "clockify_invoice_client_work": Risk.BUSINESS_WRITE,
    "clockify_record_expense": Risk.BUSINESS_WRITE,
    "clockify_request_time_off": Risk.BUSINESS_WRITE,
    "clockify_schedule_work": Risk.BUSINESS_WRITE,
    "clockify_setup_webhook": Risk.EXTERNAL_SIDE_EFFECT,
    "clockify_demo_cleanup": Risk.DESTRUCTIVE,
    # Raw write tools.
    "clockify_tags_create": Risk.BUSINESS_WRITE,
    "clockify_tags_update": Risk.BUSINESS_WRITE,
    "clockify_tags_delete": Risk.DESTRUCTIVE,
    "clockify_time_entries_create": Risk.ROUTINE_WRITE,
    "clockify_time_entries_create_for_user": Risk.ROUTINE_WRITE,
    "clockify_time_entries_update": Risk.ROUTINE_WRITE,
    "clockify_time_entries_duplicate": Risk.ROUTINE_WRITE,
    "clockify_time_entries_stop_timer": Risk.ROUTINE_WRITE,
    "clockify_time_entries_mark_invoiced": Risk.BUSINESS_WRITE,
    "clockify_time_entries_bulk_update_for_user": Risk.BUSINESS_WRITE,
    "clockify_time_entries_delete": Risk.DESTRUCTIVE,
    "clockify_time_entries_delete_all_for_user": Risk.DESTRUCTIVE,
    "clockify_approvals_resubmit": Risk.BUSINESS_WRITE,
    "clockify_approvals_resubmit_for_user": Risk.BUSINESS_WRITE,
    "clockify_approvals_submit": Risk.BUSINESS_WRITE,
    "clockify_approvals_submit_for_user": Risk.BUSINESS_WRITE,
    "clockify_approvals_submit_for_user_with_type": Risk.BUSINESS_WRITE,
    "clockify_approvals_submit_with_type": Risk.BUSINESS_WRITE,
    "clockify_approvals_update_status": Risk.BUSINESS_WRITE,
    "clockify_clients_create": Risk.BUSINESS_WRITE,
    "clockify_clients_delete": Risk.DESTRUCTIVE,
    "clockify_clients_update": Risk.BUSINESS_WRITE,
    "clockify_custom_fields_create_for_workspace": Risk.BUSINESS_WRITE,
    "clockify_custom_fields_delete_for_workspace": Risk.DESTRUCTIVE,
    "clockify_custom_fields_remove_from_project": Risk.DESTRUCTIVE,
    "clockify_custom_fields_update_for_project": Risk.BUSINESS_WRITE,
    "clockify_custom_fields_update_for_workspace": Risk.BUSINESS_WRITE,
    "clockify_expense_categories_create": Risk.BUSINESS_WRITE,
    "clockify_expense_categories_delete": Risk.DESTRUCTIVE,
    "clockify_expense_categories_update": Risk.BUSINESS_WRITE,
    "clockify_expense_categories_update_status": Risk.BUSINESS_WRITE,
    "clockify_expenses_create": Risk.BUSINESS_WRITE,
    "clockify_expenses_delete": Risk.DESTRUCTIVE,
    "clockify_expenses_update": Risk.BUSINESS_WRITE,
    "clockify_holidays_create": Risk.BUSINESS_WRITE,
    "clockify_holidays_delete": Risk.DESTRUCTIVE,
    "clockify_holidays_update": Risk.BUSINESS_WRITE,
    "clockify_invoice_items_create": Risk.BUSINESS_WRITE,
    "clockify_invoice_items_delete": Risk.DESTRUCTIVE,
    "clockify_invoice_items_import_items": Risk.BUSINESS_WRITE,
    "clockify_invoice_payments_create": Risk.BUSINESS_WRITE,
    "clockify_invoice_payments_delete": Risk.DESTRUCTIVE,
    "clockify_invoice_settings_update": Risk.BUSINESS_WRITE,
    "clockify_invoices_create": Risk.BUSINESS_WRITE,
    "clockify_invoices_delete": Risk.DESTRUCTIVE,
    "clockify_invoices_duplicate": Risk.BUSINESS_WRITE,
    "clockify_invoices_update": Risk.BUSINESS_WRITE,
    "clockify_invoices_update_status": Risk.BUSINESS_WRITE,
    "clockify_member_profiles_update": Risk.BUSINESS_WRITE,
    "clockify_projects_create": Risk.BUSINESS_WRITE,
    "clockify_projects_create_from_template": Risk.BUSINESS_WRITE,
    "clockify_projects_delete": Risk.DESTRUCTIVE,
    "clockify_projects_set_members": Risk.PRIVILEGED,
    "clockify_projects_update": Risk.BUSINESS_WRITE,
    "clockify_projects_update_estimate": Risk.BUSINESS_WRITE,
    "clockify_projects_update_memberships": Risk.PRIVILEGED,
    "clockify_projects_update_template": Risk.BUSINESS_WRITE,
    "clockify_projects_update_user_cost_rate": Risk.BUSINESS_WRITE,
    "clockify_projects_update_user_hourly_rate": Risk.BUSINESS_WRITE,
    "clockify_scheduling_change_recurring_period": Risk.BUSINESS_WRITE,
    "clockify_scheduling_copy_assignment": Risk.BUSINESS_WRITE,
    "clockify_scheduling_create_recurring": Risk.BUSINESS_WRITE,
    "clockify_scheduling_delete_recurring": Risk.DESTRUCTIVE,
    "clockify_scheduling_publish_assignments": Risk.BUSINESS_WRITE,
    "clockify_scheduling_update_recurring": Risk.BUSINESS_WRITE,
    "clockify_shared_reports_create": Risk.EXTERNAL_SIDE_EFFECT,
    "clockify_shared_reports_delete": Risk.DESTRUCTIVE,
    "clockify_shared_reports_update": Risk.EXTERNAL_SIDE_EFFECT,
    "clockify_tasks_create": Risk.BUSINESS_WRITE,
    "clockify_tasks_delete": Risk.DESTRUCTIVE,
    "clockify_tasks_update": Risk.BUSINESS_WRITE,
    "clockify_tasks_update_billable_rate": Risk.BUSINESS_WRITE,
    "clockify_tasks_update_cost_rate": Risk.BUSINESS_WRITE,
    "clockify_time_off_balance_assignments_create": Risk.BUSINESS_WRITE,
    "clockify_time_off_balance_assignments_delete": Risk.DESTRUCTIVE,
    "clockify_time_off_balance_assignments_update": Risk.BUSINESS_WRITE,
    "clockify_time_off_balances_update_for_policy": Risk.BUSINESS_WRITE,
    "clockify_time_off_policies_create": Risk.BUSINESS_WRITE,
    "clockify_time_off_policies_delete": Risk.DESTRUCTIVE,
    "clockify_time_off_policies_update": Risk.BUSINESS_WRITE,
    "clockify_time_off_policies_update_status": Risk.BUSINESS_WRITE,
    "clockify_time_off_requests_submit": Risk.BUSINESS_WRITE,
    "clockify_time_off_requests_submit_for_user": Risk.BUSINESS_WRITE,
    "clockify_time_off_requests_update_status": Risk.BUSINESS_WRITE,
    "clockify_time_off_requests_withdraw": Risk.DESTRUCTIVE,
    "clockify_user_groups_add_members": Risk.PRIVILEGED,
    "clockify_user_groups_create": Risk.BUSINESS_WRITE,
    "clockify_user_groups_delete": Risk.DESTRUCTIVE,
    "clockify_user_groups_remove_member": Risk.PRIVILEGED,
    "clockify_user_groups_update": Risk.BUSINESS_WRITE,
    "clockify_users_add_limited_to_workspace": Risk.PRIVILEGED,
    "clockify_users_add_to_workspace": Risk.PRIVILEGED,
    "clockify_users_grant_manager_role": Risk.PRIVILEGED,
    "clockify_users_revoke_manager_role": Risk.PRIVILEGED,
    "clockify_users_update_cost_rate": Risk.BUSINESS_WRITE,
    "clockify_users_update_custom_field_value": Risk.BUSINESS_WRITE,
    "clockify_users_update_hourly_rate": Risk.BUSINESS_WRITE,
    "clockify_users_update_status": Risk.PRIVILEGED,
    "clockify_webhooks_create": Risk.EXTERNAL_SIDE_EFFECT,
    "clockify_webhooks_delete": Risk.DESTRUCTIVE,
    "clockify_webhooks_rotate_token": Risk.EXTERNAL_SIDE_EFFECT,
    "clockify_webhooks_update": Risk.EXTERNAL_SIDE_EFFECT,
    "clockify_workspaces_update_billable_rate": Risk.BUSINESS_WRITE,
    "clockify_workspaces_update_cost_rate": Risk.BUSINESS_WRITE,
}

RISK_BY_TOOL: dict[str, Risk] = {
    **dict.fromkeys(_READ_TOOLS + _READ_WORKFLOWS, Risk.READ),
    **_WRITE_TOOLS,
}
