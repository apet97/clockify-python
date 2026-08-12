"""Operation records for the `time_off_requests` resource.

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

# Non-mutating search POST; items arrive under the `requests` envelope key.
TIME_OFF_REQUESTS_LIST = Operation(
    operation_id="getAllTimeOffRequestsOnWorkspace",
    resource="time_off_requests",
    sdk_method="list",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/requests",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# Period shape is policy-unit-dependent: DAYS wants {start,days}; HOURS wants {start,end}.
TIME_OFF_REQUESTS_SUBMIT = Operation(
    operation_id="createTimeOffRequest",
    resource="time_off_requests",
    sdk_method="submit",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies/{policyId}/requests",
    path_parameters=("workspaceId", "policyId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# Period shape is policy-unit-dependent: DAYS wants {start,days}; HOURS wants {start,end}.
TIME_OFF_REQUESTS_SUBMIT_FOR_USER = Operation(
    operation_id="createTimeOffRequestForUser",
    resource="time_off_requests",
    sdk_method="submit_for_user",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies/{policyId}/users/{userId}/requests",
    path_parameters=("workspaceId", "policyId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# Wire field is `status`; only APPROVED / REJECTED are valid targets.
TIME_OFF_REQUESTS_UPDATE_STATUS = Operation(
    operation_id="changeTimeOffRequestStatus",
    resource="time_off_requests",
    sdk_method="update_status",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies/{policyId}/requests/{requestId}",
    path_parameters=("workspaceId", "policyId", "requestId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.TRANSITION,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# Policy-scoped DELETE only; the flat /time-off/requests/{requestId} route 404s.
TIME_OFF_REQUESTS_WITHDRAW = Operation(
    operation_id="deleteTimeOffRequest",
    resource="time_off_requests",
    sdk_method="withdraw",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-off/policies/{policyId}/requests/{requestId}",
    path_parameters=("workspaceId", "policyId", "requestId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
        lifecycle="pending_only",
    ),
)

OPERATIONS = (
    TIME_OFF_REQUESTS_LIST,
    TIME_OFF_REQUESTS_SUBMIT,
    TIME_OFF_REQUESTS_SUBMIT_FOR_USER,
    TIME_OFF_REQUESTS_UPDATE_STATUS,
    TIME_OFF_REQUESTS_WITHDRAW,
)
