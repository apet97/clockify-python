"""Operation records for the `clients` resource.

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

# ccEmails and currencyId are silently ignored on create; only PUT persists them.
CLIENTS_CREATE = Operation(
    operation_id="postWorkspacesWorkspaceIdClients",
    resource="clients",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/clients",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# 200 answers with the full deleted entity (unlike empty-bodied deletes elsewhere).
CLIENTS_DELETE = Operation(
    operation_id="deleteWorkspacesWorkspaceIdClientsClientId",
    resource="clients",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/clients/{clientId}",
    path_parameters=("workspaceId", "clientId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
        lifecycle="archive_before_delete",
    ),
)

CLIENTS_GET = Operation(
    operation_id="getWorkspacesWorkspaceIdClientsClientId",
    resource="clients",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/clients/{clientId}",
    path_parameters=("workspaceId", "clientId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

CLIENTS_LIST = Operation(
    operation_id="getWorkspacesWorkspaceIdClients",
    resource="clients",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/clients",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("name", "name"),
        QueryParameter("archived", "archived"),
        QueryParameter("address", "address"),
        QueryParameter("note", "note"),
        QueryParameter("sort_column", "sort-column"),
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

# Replacing PUT: omitted ccEmails clears stored addresses; currencyCode inert, currencyId works only here.
CLIENTS_UPDATE = Operation(
    operation_id="putWorkspacesWorkspaceIdClientsClientId",
    resource="clients",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/clients/{clientId}",
    path_parameters=("workspaceId", "clientId"),
    query_parameters=(
        QueryParameter("archive_projects", "archive-projects"),
        QueryParameter("mark_tasks_as_done", "mark-tasks-as-done"),
    ),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.FULL_REPLACE_PROVEN,
        replacement_required_fields=("name", "ccEmails"),
    ),
)

OPERATIONS = (
    CLIENTS_CREATE,
    CLIENTS_DELETE,
    CLIENTS_GET,
    CLIENTS_LIST,
    CLIENTS_UPDATE,
)
