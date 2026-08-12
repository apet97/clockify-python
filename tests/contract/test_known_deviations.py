"""One focused regression per retained Clockify deviation class.

Each test pins the encoding of a proven live behavior into the registry or the
public surface, named after the real failure mode it prevents. Behavior-level
request/response wiring is proven per operation in tests/contract/wiring/.
"""

from clockify.operations.model import (
    MutationEffect,
    ReplacementSemantics,
    RequestEncoding,
    Service,
)
from clockify.operations.registry import ALL_OPERATIONS, BY_ID


def test_thirteen_post_reads_are_not_classified_by_verb() -> None:
    """x-clockify-risk mislabels 12 of these as writes; semantics own the truth."""
    post_reads = sorted(
        op.operation_id
        for op in ALL_OPERATIONS
        if not op.semantics.mutates and op.http_method == "POST"
    )
    assert post_reads == [
        "filterInvoices",
        "filterWorkspaceUsers",
        "generateAttendanceReport",
        "generateDetailedReport",
        "generateDetailedReportV1",
        "generateSummaryReport",
        "generateWeeklyReport",
        "getAllTimeOffRequestsOnWorkspace",
        "getMultipleTimeEntries",
        "getScheduledAssignmentsPerProject",
        "getUsersCapacityTotals",
        "getWebhookLogs",
        "searchAuditLogs",
    ]


def test_audit_log_lives_on_its_own_host() -> None:
    assert BY_ID["searchAuditLogs"].service is Service.AUDIT_LOG


def test_reports_and_shared_reports_use_reports_host() -> None:
    reports_ops = [op for op in ALL_OPERATIONS if op.service is Service.REPORTS]
    assert {op.resource for op in reports_ops} == {"reports", "shared_reports"}
    assert len(reports_ops) == 10


def test_page_size_wire_names_vary_per_operation() -> None:
    """page-size vs pageSize vs size: a global assumption would break real calls."""
    by_size_name: dict[str, set[str]] = {}
    for op in ALL_OPERATIONS:
        if op.pagination is not None:
            by_size_name.setdefault(op.pagination.page_size_parameter, set()).add(op.operation_id)
    assert "page-size" in by_size_name
    assert len(by_size_name) > 1, "manifest proves multiple page-size spellings"


def test_last_page_header_is_authoritative_only_where_proven() -> None:
    stamped = {
        op.operation_id
        for op in ALL_OPERATIONS
        if op.pagination is not None and op.pagination.last_page_header
    }
    # Representatives of the live-audited Last-Page set.
    for op_id in (
        "getApprovalRequests",
        "getWorkspacesWorkspaceIdTags",
        "getWorkspacesWorkspaceIdClients",
        "listWorkspaceCustomFields",
    ):
        assert op_id in stamped, op_id


def test_archive_before_delete_is_recorded_for_project_and_client() -> None:
    assert BY_ID["deleteProject"].semantics.lifecycle == "archive_before_delete"
    assert (
        BY_ID["deleteWorkspacesWorkspaceIdClientsClientId"].semantics.lifecycle
        == "archive_before_delete"
    )


def test_task_delete_requires_done_status() -> None:
    assert BY_ID["deleteTaskFromProject"].semantics.lifecycle == "done_before_delete"


def test_time_off_withdrawal_is_pending_only() -> None:
    assert BY_ID["deleteTimeOffRequest"].semantics.lifecycle == "pending_only"


def test_full_replacement_operations_record_their_loss_prone_fields() -> None:
    """Omitting these fields on PUT silently destroys data; the record names them."""
    assert (
        "ccEmails"
        in BY_ID["putWorkspacesWorkspaceIdClientsClientId"].semantics.replacement_required_fields
    )
    assert (
        "archived"
        in BY_ID["putWorkspacesWorkspaceIdTagsTagId"].semantics.replacement_required_fields
    )


def test_unproven_put_omission_rules_stay_conservative() -> None:
    """No PUT is assumed to be a full replace or a patch without evidence."""
    conservative = [
        op
        for op in ALL_OPERATIONS
        if op.semantics.replacement is ReplacementSemantics.UNKNOWN_CONSERVATIVE
    ]
    assert conservative, "manifest marks several PUTs unresolved"
    for op in conservative:
        assert op.semantics.mutates, op.operation_id


def test_expense_multipart_encoding_is_recorded() -> None:
    assert BY_ID["createExpense"].request_encoding is RequestEncoding.MULTIPART
    assert BY_ID["updateExpense"].request_encoding is RequestEncoding.MULTIPART


def test_stop_timer_route_is_the_user_scoped_patch() -> None:
    """The old /time-entries/stop route is a phantom 404."""
    op = BY_ID["patchWorkspacesWorkspaceIdUserUserIdTimeEntries"]
    assert op.path == "/workspaces/{workspaceId}/user/{userId}/time-entries"
    assert op.http_method == "PATCH"
    assert op.semantics.effect is MutationEffect.PATCH


def test_time_off_status_and_delete_routes_are_policy_scoped() -> None:
    """The flat /time-off/requests/{id} routes 404; only policy-scoped paths work."""
    assert "policyId" in BY_ID["changeTimeOffRequestStatus"].path_parameters
    assert "policyId" in BY_ID["deleteTimeOffRequest"].path_parameters


def test_balance_assignment_delete_carries_a_json_body() -> None:
    op = BY_ID["deleteBalanceAssignment"]
    assert op.http_method == "DELETE"
    assert op.request_encoding is RequestEncoding.JSON


def test_invoice_payment_create_returns_invoice_not_payment() -> None:
    """The 201 body is the updated invoice; the payment ID must be recovered by diffing."""
    import inspect

    from clockify.resources.invoice_payments import InvoicePaymentsResource

    doc = inspect.getdoc(InvoicePaymentsResource.create) or ""
    assert "invoice" in doc.lower()

    from clockify.models import InvoiceDtoFull

    signature = inspect.signature(InvoicePaymentsResource.create)
    assert signature.return_annotation in ("InvoiceDtoFull", InvoiceDtoFull)


def test_weekly_report_operation_exists_with_json_body() -> None:
    """Weekly reports demand an exact seven-day interval; the workflow enforces it."""
    op = BY_ID["generateWeeklyReport"]
    assert op.request_encoding is RequestEncoding.JSON
    assert not op.semantics.mutates
