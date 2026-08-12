"""Operation records for the `time_off_policies` resource.

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

# `approve` is required on create despite the spec marking it optional.
TIME_OFF_POLICIES_CREATE = Operation(
    operation_id="createTimeOffPolicy",
    resource="time_off_policies",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_OFF_POLICIES_DELETE = Operation(
    operation_id="deleteTimeOffPolicy",
    resource="time_off_policies",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies/{policyId}",
    path_parameters=("workspaceId", "policyId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_OFF_POLICIES_GET = Operation(
    operation_id="getTimeOffPolicy",
    resource="time_off_policies",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies/{policyId}",
    path_parameters=("workspaceId", "policyId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_OFF_POLICIES_LIST = Operation(
    operation_id="getTimeOffPolicies",
    resource="time_off_policies",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("name", "name"),
        QueryParameter("status", "status"),
        QueryParameter("sort_column", "sort-column"),
        QueryParameter("sort_order", "sort-order"),
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

# PUT wants `users`/`userGroups` as {contains,ids,status:"ACTIVE"} filters; GET echoes them flat.
TIME_OFF_POLICIES_UPDATE = Operation(
    operation_id="updateTimeOffPolicy",
    resource="time_off_policies",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies/{policyId}",
    path_parameters=("workspaceId", "policyId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.FULL_REPLACE_PROVEN,
    ),
)

TIME_OFF_POLICIES_UPDATE_STATUS = Operation(
    operation_id="changeTimeOffPolicyStatus",
    resource="time_off_policies",
    sdk_method="update_status",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies/{policyId}",
    path_parameters=("workspaceId", "policyId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.TRANSITION,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

OPERATIONS = (
    TIME_OFF_POLICIES_CREATE,
    TIME_OFF_POLICIES_DELETE,
    TIME_OFF_POLICIES_GET,
    TIME_OFF_POLICIES_LIST,
    TIME_OFF_POLICIES_UPDATE,
    TIME_OFF_POLICIES_UPDATE_STATUS,
)
