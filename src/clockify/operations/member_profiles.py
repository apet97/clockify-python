"""Operation records for the `member_profiles` resource.

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

MEMBER_PROFILES_GET = Operation(
    operation_id="getMemberProfile",
    resource="member_profiles",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/member-profile/{userId}",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

MEMBER_PROFILES_UPDATE = Operation(
    operation_id="updateMemberProfile",
    resource="member_profiles",
    sdk_method="update",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/member-profile/{userId}",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.PATCH,
    ),
)

OPERATIONS = (
    MEMBER_PROFILES_GET,
    MEMBER_PROFILES_UPDATE,
)
