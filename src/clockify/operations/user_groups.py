"""Operation records for the `user_groups` resource.

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

USER_GROUPS_ADD_MEMBERS = Operation(
    operation_id="addUsersToGroup",
    resource="user_groups",
    sdk_method="add_members",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user-groups/{groupId}/users",
    path_parameters=("workspaceId", "groupId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

USER_GROUPS_CREATE = Operation(
    operation_id="addNewGroup",
    resource="user_groups",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user-groups",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

USER_GROUPS_DELETE = Operation(
    operation_id="deleteGroup",
    resource="user_groups",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user-groups/{groupId}",
    path_parameters=("workspaceId", "groupId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

USER_GROUPS_LIST = Operation(
    operation_id="findAllGroupsOnWorkspace",
    resource="user_groups",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user-groups",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("project_id", "project-id"),
        QueryParameter("name", "name"),
        QueryParameter("sort_column", "sort-column"),
        QueryParameter("sort_order", "sort-order"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("include_team_managers", "includeTeamManagers"),
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

USER_GROUPS_REMOVE_MEMBER = Operation(
    operation_id="removeUserFromGroup",
    resource="user_groups",
    sdk_method="remove_member",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user-groups/{groupId}/users/{userId}",
    path_parameters=("workspaceId", "groupId", "userId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

USER_GROUPS_UPDATE = Operation(
    operation_id="updateGroup",
    resource="user_groups",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user-groups/{groupId}",
    path_parameters=("workspaceId", "groupId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

OPERATIONS = (
    USER_GROUPS_ADD_MEMBERS,
    USER_GROUPS_CREATE,
    USER_GROUPS_DELETE,
    USER_GROUPS_LIST,
    USER_GROUPS_REMOVE_MEMBER,
    USER_GROUPS_UPDATE,
)
