"""Operation records for the `time_off_balances` resource.

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

TIME_OFF_BALANCES_LIST_FOR_POLICY = Operation(
    operation_id="getBalancesForPolicy",
    resource="time_off_balances",
    sdk_method="list_for_policy",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/balance/policy/{policyId}",
    path_parameters=("workspaceId", "policyId"),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("sort", "sort"),
        QueryParameter("sort_order", "sort-order"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=("balances",),
        last_page_header=True,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_OFF_BALANCES_LIST_FOR_USER = Operation(
    operation_id="getBalanceForUser",
    resource="time_off_balances",
    sdk_method="list_for_user",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/balance/user/{userId}",
    path_parameters=("workspaceId", "userId"),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("sort", "sort"),
        QueryParameter("sort_order", "sort-order"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=("balances",),
        last_page_header=True,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_OFF_BALANCES_UPDATE_FOR_POLICY = Operation(
    operation_id="updateBalance",
    resource="time_off_balances",
    sdk_method="update_for_policy",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/balance/policy/{policyId}",
    path_parameters=("workspaceId", "policyId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.NONE,  # 204
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.PATCH,
    ),
)

OPERATIONS = (
    TIME_OFF_BALANCES_LIST_FOR_POLICY,
    TIME_OFF_BALANCES_LIST_FOR_USER,
    TIME_OFF_BALANCES_UPDATE_FOR_POLICY,
)
