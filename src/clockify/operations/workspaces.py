"""Operation records for the `workspaces` resource.

Hand-authored from docs/port/OPERATION_PORT_MANIFEST.md; verify against it, not
against the raw OpenAPI alone.
"""

from clockify.operations.model import (
    MutationEffect,
    Operation,
    OperationSemantics,
    QueryParameter,
    ReplacementSemantics,
    RequestEncoding,
    ResponseKind,
    Service,
)

WORKSPACES_CREATE = Operation(
    operation_id="addWorkspace",
    resource="workspaces",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces",
    path_parameters=(),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

WORKSPACES_GET = Operation(
    operation_id="getWorkspaceInfo",
    resource="workspaces",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# No server-side paging: page/page-size variants are ignored and the full collection returns.
WORKSPACES_LIST = Operation(
    operation_id="getAllMyWorkspaces",
    resource="workspaces",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces",
    path_parameters=(),
    query_parameters=(
        QueryParameter("roles", "roles"),  # repeated query key
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# Rate amount is a raw integer in minor units; no currency scaling.
WORKSPACES_UPDATE_BILLABLE_RATE = Operation(
    operation_id="updateWorkspaceBillableRate",
    resource="workspaces",
    sdk_method="update_billable_rate",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/hourly-rate",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

# Rate amount is a raw integer in minor units; no currency scaling.
WORKSPACES_UPDATE_COST_RATE = Operation(
    operation_id="updateWorkspaceCostRate",
    resource="workspaces",
    sdk_method="update_cost_rate",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/cost-rate",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

OPERATIONS = (
    WORKSPACES_CREATE,
    WORKSPACES_GET,
    WORKSPACES_LIST,
    WORKSPACES_UPDATE_BILLABLE_RATE,
    WORKSPACES_UPDATE_COST_RATE,
)
