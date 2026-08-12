"""Operation records for the `invoice_items` resource.

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

INVOICE_ITEMS_CREATE = Operation(
    operation_id="addInvoiceItem",
    resource="invoice_items",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}/items",
    path_parameters=("workspaceId", "invoiceId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # unitPrice wire scale is minor units x100; amount = unitPrice * quantity / 100

INVOICE_ITEMS_DELETE = Operation(
    operation_id="deleteInvoiceItem",
    resource="invoice_items",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}/items/{order}",
    path_parameters=("workspaceId", "invoiceId", "order"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,  # 200 returns updated InvoiceDtoFull
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # `order` path param is an int >= 1 (item order, not an id)

INVOICE_ITEMS_IMPORT_ITEMS = Operation(
    operation_id="importInvoiceItems",
    resource="invoice_items",
    sdk_method="import_items",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/{invoiceId}/items/import",
    path_parameters=("workspaceId", "invoiceId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

OPERATIONS = (
    INVOICE_ITEMS_CREATE,
    INVOICE_ITEMS_DELETE,
    INVOICE_ITEMS_IMPORT_ITEMS,
)
