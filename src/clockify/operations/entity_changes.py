"""Operation records for the `entity_changes` resource.

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

_READ = OperationSemantics(
    mutates=False,
    effect=MutationEffect.NONE,
    replacement=ReplacementSemantics.NOT_APPLICABLE,
)

# `page` and `limit` are string-typed on the wire (defaults '0' and '50').
ENTITY_CHANGES_LIST_CREATED = Operation(
    operation_id="getCreatedEntityInfo",
    resource="entity_changes",
    sdk_method="list_created",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/entities/created",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("type", "type"),
        QueryParameter("start", "start"),
        QueryParameter("end", "end"),
        QueryParameter("page", "page"),
        QueryParameter("limit", "limit"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="limit",
        items_path=None,
    ),
    semantics=_READ,
)

ENTITY_CHANGES_LIST_DELETED = Operation(
    operation_id="getDeletedEntityInfo",
    resource="entity_changes",
    sdk_method="list_deleted",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/entities/deleted",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("type", "type"),
        QueryParameter("start", "start"),
        QueryParameter("end", "end"),
        QueryParameter("page", "page"),
        QueryParameter("limit", "limit"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="limit",
        items_path=None,
    ),
    semantics=_READ,
)

ENTITY_CHANGES_LIST_UPDATED = Operation(
    operation_id="getUpdatedEntityInfo",
    resource="entity_changes",
    sdk_method="list_updated",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/entities/updated",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("type", "type"),
        QueryParameter("start", "start"),
        QueryParameter("end", "end"),
        QueryParameter("page", "page"),
        QueryParameter("limit", "limit"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="limit",
        items_path=None,
    ),
    semantics=_READ,
)

OPERATIONS = (
    ENTITY_CHANGES_LIST_CREATED,
    ENTITY_CHANGES_LIST_DELETED,
    ENTITY_CHANGES_LIST_UPDATED,
)
