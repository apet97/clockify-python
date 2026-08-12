"""Operation records for the `audit_log` resource.

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

# Non-mutating POST: the body is a search filter, not a write. Closed action enum.
AUDIT_LOG_SEARCH = Operation(
    operation_id="searchAuditLogs",
    resource="audit_log",
    sdk_method="search",
    http_method="POST",
    service=Service.AUDIT_LOG,
    path="/workspaces/{workspaceId}/audit-log",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

OPERATIONS = (AUDIT_LOG_SEARCH,)
