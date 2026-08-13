"""Operation records for the `users` resource.

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

USERS_ADD_LIMITED_TO_WORKSPACE = Operation(
    operation_id="addLimitedUsersWithInfo",
    resource="users",
    sdk_method="add_limited_to_workspace",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/limited-users",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

USERS_ADD_TO_WORKSPACE = Operation(
    operation_id="addUserToWorkspace",
    resource="users",
    sdk_method="add_to_workspace",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users",
    path_parameters=("workspaceId",),
    query_parameters=(QueryParameter("send_email", "send-email", required=True),),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# Non-mutating filter POST.
USERS_FILTER = Operation(
    operation_id="filterWorkspaceUsers",
    resource="users",
    sdk_method="filter",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users/info",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

USERS_GRANT_MANAGER_ROLE = Operation(
    operation_id="giveUserManagerRole",
    resource="users",
    sdk_method="grant_manager_role",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users/{userId}/roles",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

USERS_LIST = Operation(
    operation_id="findWorkspaceUsers",
    resource="users",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("email", "email"),
        QueryParameter("project_id", "project-id"),
        QueryParameter("status", "status"),
        QueryParameter("account_statuses", "account-statuses"),
        QueryParameter("name", "name"),
        QueryParameter("sort_column", "sort-column"),
        QueryParameter("sort_order", "sort-order"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("memberships", "memberships"),
        QueryParameter("include_roles", "include-roles", required=True),
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

USERS_LIST_MANAGERS = Operation(
    operation_id="findUserTeamManagers",
    resource="users",
    sdk_method="list_managers",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users/{userId}/managers",
    path_parameters=("workspaceId", "userId"),
    query_parameters=(
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

USERS_ME = Operation(
    operation_id="getCurrentUser",
    resource="users",
    sdk_method="me",
    http_method="GET",
    service=Service.REGULAR,
    path="/user",
    path_parameters=(),
    query_parameters=(QueryParameter("include_memberships", "include-memberships"),),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# DELETE with a required JSON body (ManagerRoleRequest); 204 no content.
USERS_REVOKE_MANAGER_ROLE = Operation(
    operation_id="removeUserManagerRole",
    resource="users",
    sdk_method="revoke_manager_role",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users/{userId}/roles",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# Rate amount is a raw integer in minor units; GET on rate paths 405s.
USERS_UPDATE_COST_RATE = Operation(
    operation_id="updateUserCostRate",
    resource="users",
    sdk_method="update_cost_rate",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users/{userId}/cost-rate",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

USERS_UPDATE_CUSTOM_FIELD_VALUE = Operation(
    operation_id="updateUserCustomFieldValue",
    resource="users",
    sdk_method="update_custom_field_value",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users/{userId}/custom-field/{customFieldId}/value",
    path_parameters=("workspaceId", "userId", "customFieldId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

# Rate amount is a raw integer in minor units; GET on rate paths 405s.
USERS_UPDATE_HOURLY_RATE = Operation(
    operation_id="updateUserHourlyRate",
    resource="users",
    sdk_method="update_hourly_rate",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users/{userId}/hourly-rate",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

USERS_UPDATE_STATUS = Operation(
    operation_id="updateUserStatus",
    resource="users",
    sdk_method="update_status",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/users/{userId}",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

OPERATIONS = (
    USERS_ADD_LIMITED_TO_WORKSPACE,
    USERS_ADD_TO_WORKSPACE,
    USERS_FILTER,
    USERS_GRANT_MANAGER_ROLE,
    USERS_LIST,
    USERS_LIST_MANAGERS,
    USERS_ME,
    USERS_REVOKE_MANAGER_ROLE,
    USERS_UPDATE_COST_RATE,
    USERS_UPDATE_CUSTOM_FIELD_VALUE,
    USERS_UPDATE_HOURLY_RATE,
    USERS_UPDATE_STATUS,
)
