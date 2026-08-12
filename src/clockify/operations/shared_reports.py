"""Operation records for the `shared_reports` resource.

Hand-authored from docs/port/OPERATION_PORT_MANIFEST.md; verify against it, not
against the raw OpenAPI alone.
"""

from clockify.operations.model import (
    MutationEffect,
    Operation,
    OperationSemantics,
    PaginationSpec,
    QueryParameter,
    ReplacementSemantics,
    RequestEncoding,
    ResponseKind,
    Service,
)

SHARED_REPORTS_CREATE = Operation(
    operation_id="postWorkspacesWorkspaceIdSharedReports",
    resource="shared_reports",
    sdk_method="create",
    http_method="POST",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/shared-reports",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # live wire success status is 200, not 201

SHARED_REPORTS_DELETE = Operation(
    operation_id="deleteWorkspacesWorkspaceIdSharedReportsSharedReportId",
    resource="shared_reports",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/shared-reports/{sharedReportId}",
    path_parameters=("workspaceId", "sharedReportId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

SHARED_REPORTS_LIST = Operation(
    operation_id="getWorkspacesWorkspaceIdSharedReports",
    resource="shared_reports",
    sdk_method="list",
    http_method="GET",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/shared-reports",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("page_size", "pageSize"),  # camelCase on the reports host
        QueryParameter("shared_reports_filter", "sharedReportsFilter"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="pageSize",
        items_path=("reports",),
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

SHARED_REPORTS_UPDATE = Operation(
    operation_id="putWorkspacesWorkspaceIdSharedReportsSharedReportId",
    resource="shared_reports",
    sdk_method="update",
    http_method="PUT",
    service=Service.REPORTS,
    path="/workspaces/{workspaceId}/shared-reports/{sharedReportId}",
    path_parameters=("workspaceId", "sharedReportId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.PATCH,
    ),
)  # PUT with documented merge semantics, not a full replace

SHARED_REPORTS_VIEW_PUBLIC = Operation(
    operation_id="getSharedReportsSharedReportId",
    resource="shared_reports",
    sdk_method="view_public",
    http_method="GET",
    service=Service.REPORTS,
    path="/shared-reports/{sharedReportId}",
    path_parameters=("sharedReportId",),
    query_parameters=(
        QueryParameter("export_type", "exportType"),
        QueryParameter("date_range_start", "dateRangeStart"),
        QueryParameter("date_range_end", "dateRangeEnd"),
        QueryParameter("sort_column", "sortColumn"),
        QueryParameter("sort_order", "sortOrder"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "pageSize"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.CONTENT_NEGOTIATED,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="pageSize",
        items_path=("groupOne",),  # envelope also carries totals and donutChart arrays
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

OPERATIONS = (
    SHARED_REPORTS_CREATE,
    SHARED_REPORTS_DELETE,
    SHARED_REPORTS_LIST,
    SHARED_REPORTS_UPDATE,
    SHARED_REPORTS_VIEW_PUBLIC,
)
