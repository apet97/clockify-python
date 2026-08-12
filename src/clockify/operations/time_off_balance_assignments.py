"""Operation records for the `time_off_balance_assignments` resource.

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

TIME_OFF_BALANCE_ASSIGNMENTS_CREATE = Operation(
    operation_id="createBalanceAssignment",
    resource="time_off_balance_assignments",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/balance/assignment",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.NONE,  # 201 with empty body
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # additive, not idempotent: create adds to an existing (user, policy) assignment

TIME_OFF_BALANCE_ASSIGNMENTS_DELETE = Operation(
    operation_id="deleteBalanceAssignment",
    resource="time_off_balance_assignments",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path=(
        "/workspaces/{workspaceId}/time-off/balance/assignment/{balanceAssignmentId}"
        "/user/{userId}/policy/{policyId}"
    ),
    path_parameters=("workspaceId", "balanceAssignmentId", "userId", "policyId"),
    request_encoding=RequestEncoding.JSON,  # DELETE with a required JSON body
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_OFF_BALANCE_ASSIGNMENTS_GET_FOR_USER_AND_POLICY = Operation(
    operation_id="getBalanceAssignmentsForUserAndPolicy",
    resource="time_off_balance_assignments",
    sdk_method="get_for_user_and_policy",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/balance/assignment/user/{userId}/policy/{policyId}",
    path_parameters=("workspaceId", "userId", "policyId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_OFF_BALANCE_ASSIGNMENTS_UPDATE = Operation(
    operation_id="updateBalanceAssignment",
    resource="time_off_balance_assignments",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path=(
        "/workspaces/{workspaceId}/time-off/balance/assignment/{balanceAssignmentId}"
        "/user/{userId}/policy/{policyId}"
    ),
    path_parameters=("workspaceId", "balanceAssignmentId", "userId", "policyId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.NONE,  # 204
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)  # `balanceChange` is applied as a delta, not a replacement value

OPERATIONS = (
    TIME_OFF_BALANCE_ASSIGNMENTS_CREATE,
    TIME_OFF_BALANCE_ASSIGNMENTS_DELETE,
    TIME_OFF_BALANCE_ASSIGNMENTS_GET_FOR_USER_AND_POLICY,
    TIME_OFF_BALANCE_ASSIGNMENTS_UPDATE,
)
