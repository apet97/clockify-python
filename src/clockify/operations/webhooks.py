"""Operation records for the `webhooks` resource.

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

# `name` required only under X-Api-Key auth, not under X-Addon-Token.
WEBHOOKS_CREATE = Operation(
    operation_id="createWebhook",
    resource="webhooks",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/webhooks",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

WEBHOOKS_DELETE = Operation(
    operation_id="deleteWebhook",
    resource="webhooks",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/webhooks/{webhookId}",
    path_parameters=("workspaceId", "webhookId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

WEBHOOKS_GET = Operation(
    operation_id="getWebhookById",
    resource="webhooks",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/webhooks/{webhookId}",
    path_parameters=("workspaceId", "webhookId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

WEBHOOKS_LIST = Operation(
    operation_id="getWebhooksOnWorkspace",
    resource="webhooks",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/webhooks",
    path_parameters=("workspaceId",),
    query_parameters=(QueryParameter("type", "type"),),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

WEBHOOKS_LIST_EVENT_STATUSES = Operation(
    operation_id="getWebhookEventStatusesWithLatestLog",
    resource="webhooks",
    sdk_method="list_event_statuses",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/webhooks/{webhookId}/statuses",
    path_parameters=("workspaceId", "webhookId"),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("size", "size"),
        QueryParameter("statuses", "statuses"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="size",
        items_path=None,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

WEBHOOKS_LIST_FOR_ADDON = Operation(
    operation_id="getAddonWebhooksOnWorkspace",
    resource="webhooks",
    sdk_method="list_for_addon",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/addons/{addonId}/webhooks",
    path_parameters=("workspaceId", "addonId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# Body-less PATCH that regenerates the webhook token.
WEBHOOKS_ROTATE_TOKEN = Operation(
    operation_id="patchWorkspacesWorkspaceIdWebhooksWebhookIdToken",
    resource="webhooks",
    sdk_method="rotate_token",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/webhooks/{webhookId}/token",
    path_parameters=("workspaceId", "webhookId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# Non-mutating log-search POST with query-string pagination.
WEBHOOKS_SEARCH_LOGS = Operation(
    operation_id="getWebhookLogs",
    resource="webhooks",
    sdk_method="search_logs",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/webhooks/{webhookId}/logs",
    path_parameters=("workspaceId", "webhookId"),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("size", "size"),
    ),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="size",
        items_path=None,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

WEBHOOKS_UPDATE = Operation(
    operation_id="updateWebhook",
    resource="webhooks",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/webhooks/{webhookId}",
    path_parameters=("workspaceId", "webhookId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

OPERATIONS = (
    WEBHOOKS_CREATE,
    WEBHOOKS_DELETE,
    WEBHOOKS_GET,
    WEBHOOKS_LIST,
    WEBHOOKS_LIST_EVENT_STATUSES,
    WEBHOOKS_LIST_FOR_ADDON,
    WEBHOOKS_ROTATE_TOKEN,
    WEBHOOKS_SEARCH_LOGS,
    WEBHOOKS_UPDATE,
)
