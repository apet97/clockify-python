"""Operation records for the `approvals` resource.

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

APPROVALS_LIST = Operation(
    operation_id="getApprovalRequests",
    resource="approvals",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/approval-requests",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("status", "status"),
        QueryParameter("sort_column", "sort-column"),
        QueryParameter("types", "types"),
        QueryParameter("sort_order", "sort-order"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=None,
        last_page_header=True,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

APPROVALS_RESUBMIT = Operation(
    operation_id="resubmitEntriesForApproval",
    resource="approvals",
    sdk_method="resubmit",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/approval-requests/resubmit-entries-for-approval",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

APPROVALS_RESUBMIT_FOR_USER = Operation(
    operation_id="resubmitEntriesForApprovalForUser",
    resource="approvals",
    sdk_method="resubmit_for_user",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/approval-requests/users/{userId}/resubmit-entries-for-approval",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

APPROVALS_SUBMIT = Operation(
    operation_id="submitApprovalRequest",
    resource="approvals",
    sdk_method="submit",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/approval-requests",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

APPROVALS_SUBMIT_FOR_USER = Operation(
    operation_id="submitApprovalRequestForUser",
    resource="approvals",
    sdk_method="submit_for_user",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/approval-requests/users/{userId}",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

APPROVALS_SUBMIT_FOR_USER_WITH_TYPE = Operation(
    operation_id="createApprovalForOtherWithType",
    resource="approvals",
    sdk_method="submit_for_user_with_type",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/approval-requests/users/{userId}/{type}",
    path_parameters=("workspaceId", "userId", "type"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# `approvalRequestId` path segment is actually the approval type (TIMESHEET | EXPENSE);
# the name collides at the routing level with PATCH .../approval-requests/{approvalRequestId}.
APPROVALS_SUBMIT_WITH_TYPE = Operation(
    operation_id="createApprrovalRequest_1",
    resource="approvals",
    sdk_method="submit_with_type",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/approval-requests/{approvalRequestId}",
    path_parameters=("workspaceId", "approvalRequestId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

APPROVALS_UPDATE_STATUS = Operation(
    operation_id="updateApprovalRequest",
    resource="approvals",
    sdk_method="update_status",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/approval-requests/{approvalRequestId}",
    path_parameters=("workspaceId", "approvalRequestId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.PATCH,
    ),
)

OPERATIONS = (
    APPROVALS_LIST,
    APPROVALS_RESUBMIT,
    APPROVALS_RESUBMIT_FOR_USER,
    APPROVALS_SUBMIT,
    APPROVALS_SUBMIT_FOR_USER,
    APPROVALS_SUBMIT_FOR_USER_WITH_TYPE,
    APPROVALS_SUBMIT_WITH_TYPE,
    APPROVALS_UPDATE_STATUS,
)
