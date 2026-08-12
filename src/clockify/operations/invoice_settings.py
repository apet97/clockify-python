"""Operation records for the `invoice_settings` resource.

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

INVOICE_SETTINGS_GET = Operation(
    operation_id="getInvoiceSettings",
    resource="invoice_settings",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/settings",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

INVOICE_SETTINGS_UPDATE = Operation(
    operation_id="updateInvoiceSettings",
    resource="invoice_settings",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/invoices/settings",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.NONE,  # 200 with empty body
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.FULL_REPLACE_PROVEN,
    ),
)  # workspace-wide configuration replace

OPERATIONS = (
    INVOICE_SETTINGS_GET,
    INVOICE_SETTINGS_UPDATE,
)
