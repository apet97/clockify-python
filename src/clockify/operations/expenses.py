"""Operation records for the `expenses` resource.

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

EXPENSES_CREATE = Operation(
    operation_id="createExpense",
    resource="expenses",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.MULTIPART,  # `file` part is application/octet-stream
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # request `amount` is MAJOR units (dollars); response `total` is MINOR (cents)

EXPENSES_DELETE = Operation(
    operation_id="deleteExpense",
    resource="expenses",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses/{expenseId}",
    path_parameters=("workspaceId", "expenseId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.NONE,  # 200 with empty body
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

EXPENSES_DOWNLOAD_RECEIPT = Operation(
    operation_id="downloadExpenseReceipt",
    resource="expenses",
    sdk_method="download_receipt",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses/{expenseId}/files/{fileId}",
    path_parameters=("workspaceId", "expenseId", "fileId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.BYTES,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

EXPENSES_GET = Operation(
    operation_id="getExpenseById",
    resource="expenses",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses/{expenseId}",
    path_parameters=("workspaceId", "expenseId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

EXPENSES_LIST = Operation(
    operation_id="getWorkspaceExpenses",
    resource="expenses",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("user_id", "user-id"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=("expenses", "expenses"),  # double-nested envelope; see fixture notes
        last_page_header=True,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

EXPENSES_UPDATE = Operation(
    operation_id="updateExpense",
    resource="expenses",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/expenses/{expenseId}",
    path_parameters=("workspaceId", "expenseId"),
    request_encoding=RequestEncoding.MULTIPART,  # `file` part is application/octet-stream
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.FULL_REPLACE_PROVEN,
    ),
)  # request `amount` is MAJOR units (dollars); response `total` is MINOR (cents)

OPERATIONS = (
    EXPENSES_CREATE,
    EXPENSES_DELETE,
    EXPENSES_DOWNLOAD_RECEIPT,
    EXPENSES_GET,
    EXPENSES_LIST,
    EXPENSES_UPDATE,
)
