"""Operation records for the `expense_categories` resource.

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

EXPENSE_CATEGORIES_CREATE = Operation(
    operation_id="addExpenseCategory",
    resource="expense_categories",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses/categories",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

EXPENSE_CATEGORIES_DELETE = Operation(
    operation_id="deleteExpenseCategory",
    resource="expense_categories",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses/categories/{categoryId}",
    path_parameters=("workspaceId", "categoryId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
        lifecycle="archive_before_delete",
    ),
)

EXPENSE_CATEGORIES_LIST = Operation(
    operation_id="getExpenseCategories",
    resource="expense_categories",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses/categories",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("sort_column", "sort-column"),
        QueryParameter("sort_order", "sort-order"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("archived", "archived"),
        QueryParameter("name", "name"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=("categories",),
        last_page_header=True,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

EXPENSE_CATEGORIES_UPDATE = Operation(
    operation_id="updateExpenseCategory",
    resource="expense_categories",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses/categories/{categoryId}",
    path_parameters=("workspaceId", "categoryId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.FULL_REPLACE_PROVEN,
    ),
)

EXPENSE_CATEGORIES_UPDATE_STATUS = Operation(
    operation_id="archiveExpenseCategory",
    resource="expense_categories",
    sdk_method="update_status",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses/categories/{categoryId}/status",
    path_parameters=("workspaceId", "categoryId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.TRANSITION,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

OPERATIONS = (
    EXPENSE_CATEGORIES_CREATE,
    EXPENSE_CATEGORIES_DELETE,
    EXPENSE_CATEGORIES_LIST,
    EXPENSE_CATEGORIES_UPDATE,
    EXPENSE_CATEGORIES_UPDATE_STATUS,
)
