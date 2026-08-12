"""Operation records for the `invoice_payments` resource.

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

INVOICE_PAYMENTS_CREATE = Operation(
    operation_id="addInvoicePayment",
    resource="invoice_payments",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}/payments",
    path_parameters=("workspaceId", "invoiceId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # 201 returns the updated INVOICE, not the payment; recover payment id via list diff.
#    Request `amount` is int64 MINOR units (min 1); request `paymentDate` vs list `date`.

INVOICE_PAYMENTS_DELETE = Operation(
    operation_id="deleteInvoicePayment",
    resource="invoice_payments",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}/payments/{paymentId}",
    path_parameters=("workspaceId", "invoiceId", "paymentId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,  # 200 returns updated InvoiceDtoFull
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

INVOICE_PAYMENTS_LIST = Operation(
    operation_id="getInvoicePayments",
    resource="invoice_payments",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}/payments",
    path_parameters=("workspaceId", "invoiceId"),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=None,  # bare array
        last_page_header=True,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

OPERATIONS = (
    INVOICE_PAYMENTS_CREATE,
    INVOICE_PAYMENTS_DELETE,
    INVOICE_PAYMENTS_LIST,
)
