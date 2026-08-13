"""Operation records for the `invoices` resource.

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

INVOICES_CREATE = Operation(
    operation_id="addInvoice",
    resource="invoices",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # POST silently drops note/subject; create draft first, then update

INVOICES_DELETE = Operation(
    operation_id="deleteInvoice",
    resource="invoices",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}",
    path_parameters=("workspaceId", "invoiceId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

INVOICES_DUPLICATE = Operation(
    operation_id="duplicateInvoice",
    resource="invoices",
    sdk_method="duplicate",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}/duplicate",
    path_parameters=("workspaceId", "invoiceId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

INVOICES_EXPORT = Operation(
    operation_id="exportInvoice",
    resource="invoices",
    sdk_method="export",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}/export",
    path_parameters=("workspaceId", "invoiceId"),
    query_parameters=(QueryParameter("user_locale", "userLocale", required=True),),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.BYTES,  # binary payload; SDK-only read
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

INVOICES_FILTER = Operation(
    operation_id="filterInvoices",
    resource="invoices",
    sdk_method="filter",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/info",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(  # non-mutating POST
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

INVOICES_GET = Operation(
    operation_id="getInvoiceById",
    resource="invoices",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}",
    path_parameters=("workspaceId", "invoiceId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

INVOICES_LIST = Operation(
    operation_id="getWorkspaceInvoices",
    resource="invoices",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("statuses", "statuses"),  # repeated query key
        QueryParameter("sort_column", "sort-column"),
        QueryParameter("sort_order", "sort-order"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=("invoices",),
        last_page_header=True,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

INVOICES_UPDATE = Operation(
    operation_id="updateInvoice",
    resource="invoices",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}",
    path_parameters=("workspaceId", "invoiceId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.FULL_REPLACE_PROVEN,
    ),
)  # PUT replaces whole document; GET returns tax/tax2/discount x100, PUT wants taxPercent/tax2Percent/discountPercent as plain percents

INVOICES_UPDATE_STATUS = Operation(
    operation_id="changeInvoiceStatus",
    resource="invoices",
    sdk_method="update_status",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}/status",
    path_parameters=("workspaceId", "invoiceId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.TRANSITION,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

OPERATIONS = (
    INVOICES_CREATE,
    INVOICES_DELETE,
    INVOICES_DUPLICATE,
    INVOICES_EXPORT,
    INVOICES_FILTER,
    INVOICES_GET,
    INVOICES_LIST,
    INVOICES_UPDATE,
    INVOICES_UPDATE_STATUS,
)
