"""Operation records for the `reports` resource.

Hand-authored from docs/port/OPERATION_PORT_MANIFEST.md; verify against it, not
against the raw OpenAPI alone.
"""

from clockify.operations.model import (
    MutationEffect,
    Operation,
    OperationSemantics,
    ReplacementSemantics,
    RequestEncoding,
    ResponseKind,
    Service,
)

REPORTS_ATTENDANCE = Operation(
    operation_id="generateAttendanceReport",
    resource="reports",
    sdk_method="attendance",
    http_method="POST",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/reports/attendance",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

REPORTS_DETAILED = Operation(
    operation_id="generateDetailedReport",
    resource="reports",
    sdk_method="detailed",
    http_method="POST",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/reports/detailed",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

REPORTS_EXPENSE_DETAILS = Operation(
    operation_id="generateDetailedReportV1",
    resource="reports",
    sdk_method="expense_details",
    http_method="POST",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/reports/expenses/detailed",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,  # body optional on the wire
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

REPORTS_SUMMARY = Operation(
    operation_id="generateSummaryReport",
    resource="reports",
    sdk_method="summary",
    http_method="POST",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/reports/summary",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

REPORTS_WEEKLY = Operation(
    operation_id="generateWeeklyReport",
    resource="reports",
    sdk_method="weekly",
    http_method="POST",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/reports/weekly",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # requires an exact seven-day dateRangeStart..dateRangeEnd interval

OPERATIONS = (
    REPORTS_ATTENDANCE,
    REPORTS_DETAILED,
    REPORTS_EXPENSE_DETAILS,
    REPORTS_SUMMARY,
    REPORTS_WEEKLY,
)
