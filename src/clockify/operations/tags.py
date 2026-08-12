"""Operation records for the `tags` resource.

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

TAGS_CREATE = Operation(
    operation_id="postWorkspacesWorkspaceIdTags",
    resource="tags",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/tags",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # a previously deleted name stays reserved; "already exists" needs a distinct name

TAGS_DELETE = Operation(
    operation_id="deleteWorkspacesWorkspaceIdTagsTagId",
    resource="tags",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/tags/{tagId}",
    path_parameters=("workspaceId", "tagId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # 200 with the full deleted Tag entity as the body

TAGS_GET = Operation(
    operation_id="getWorkspacesWorkspaceIdTagsTagId",
    resource="tags",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/tags/{tagId}",
    path_parameters=("workspaceId", "tagId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TAGS_LIST = Operation(
    operation_id="getWorkspacesWorkspaceIdTags",
    resource="tags",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/tags",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("name", "name"),
        QueryParameter("strict_name_search", "strict-name-search"),
        QueryParameter("excluded_ids", "excluded-ids"),
        QueryParameter("archived", "archived"),
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
)  # omitting archived returns archived AND active; only archived=false restricts

TAGS_UPDATE = Operation(
    operation_id="putWorkspacesWorkspaceIdTagsTagId",
    resource="tags",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/tags/{tagId}",
    path_parameters=("workspaceId", "tagId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.FULL_REPLACE_PROVEN,
        replacement_required_fields=("archived",),
    ),
)  # full replace: omitting archived resets it to false (silently un-archives)

OPERATIONS = (
    TAGS_CREATE,
    TAGS_DELETE,
    TAGS_GET,
    TAGS_LIST,
    TAGS_UPDATE,
)
