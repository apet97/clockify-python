"""Operation records for the `projects` resource.

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

PROJECTS_CREATE = Operation(
    operation_id="createProject",
    resource="projects",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # deleted names stay reserved: "already exists" even when name no longer listed

PROJECTS_CREATE_FROM_TEMPLATE = Operation(
    operation_id="createProjectFromTemplate",
    resource="projects",
    sdk_method="create_from_template",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/from-template",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

PROJECTS_DELETE = Operation(
    operation_id="deleteProject",
    resource="projects",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}",
    path_parameters=("workspaceId", "projectId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
        lifecycle="archive_before_delete",
    ),
)

PROJECTS_GET = Operation(
    operation_id="getProjectById",
    resource="projects",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}",
    path_parameters=("workspaceId", "projectId"),
    query_parameters=(
        QueryParameter("hydrated", "hydrated"),
        QueryParameter("custom_field_entity_type", "custom-field-entity-type"),
        QueryParameter("expense_limit", "expense-limit"),
        QueryParameter("expense_date", "expense-date"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # deleted/never-existing/foreign ids all return the same 400 code 501 body, never 404

PROJECTS_LIST = Operation(
    operation_id="getWorkspaceProjects",
    resource="projects",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("name", "name"),
        QueryParameter("strict_name_search", "strict-name-search"),
        QueryParameter("archived", "archived"),
        QueryParameter("billable", "billable"),
        QueryParameter("clients", "clients"),  # repeated query key
        QueryParameter("contains_client", "contains-client"),
        QueryParameter("client_status", "client-status"),
        QueryParameter("users", "users"),  # repeated query key
        QueryParameter("contains_user", "contains-user"),
        QueryParameter("user_status", "user-status"),
        QueryParameter("is_template", "is-template"),
        QueryParameter("sort_column", "sort-column"),
        QueryParameter("sort_order", "sort-order"),
        QueryParameter("hydrated", "hydrated"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("access", "access"),
        QueryParameter("expense_limit", "expense-limit"),
        QueryParameter("expense_date", "expense-date"),
        QueryParameter("user_groups", "userGroups"),  # repeated query key
        QueryParameter("contains_group", "contains-group"),
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
)  # omitting `archived` returns both archived and active; only archived=false restricts

PROJECTS_SET_MEMBERS = Operation(
    operation_id="assignOrRemoveProjectUsers",
    resource="projects",
    sdk_method="set_members",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/memberships",
    path_parameters=("workspaceId", "projectId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,  # multi-entity assign/remove
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

PROJECTS_UPDATE = Operation(
    operation_id="updateProject",
    resource="projects",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}",
    path_parameters=("workspaceId", "projectId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,  # mixed and unresolved
        replacement_required_fields=("billable", "isPublic"),
    ),
)  # GET-side `public` maps to request-side `isPublic`; rates preserved under omission

PROJECTS_UPDATE_ESTIMATE = Operation(
    operation_id="updateProjectEstimate",
    resource="projects",
    sdk_method="update_estimate",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/estimate",
    path_parameters=("workspaceId", "projectId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.PATCH,
    ),
)

PROJECTS_UPDATE_MEMBERSHIPS = Operation(
    operation_id="updateProjectMemberships",
    resource="projects",
    sdk_method="update_memberships",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/memberships",
    path_parameters=("workspaceId", "projectId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.PATCH,
    ),
)

PROJECTS_UPDATE_TEMPLATE = Operation(
    operation_id="updateProjectTemplate",
    resource="projects",
    sdk_method="update_template",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/template",
    path_parameters=("workspaceId", "projectId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.TRANSITION,  # template flag toggle
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

PROJECTS_UPDATE_USER_COST_RATE = Operation(
    operation_id="updateProjectUserCostRate",
    resource="projects",
    sdk_method="update_user_cost_rate",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/users/{userId}/cost-rate",
    path_parameters=("workspaceId", "projectId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)  # rate `amount` is integer minor units; GET on rate paths 405s

PROJECTS_UPDATE_USER_HOURLY_RATE = Operation(
    operation_id="updateProjectUserHourlyRate",
    resource="projects",
    sdk_method="update_user_hourly_rate",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/users/{userId}/hourly-rate",
    path_parameters=("workspaceId", "projectId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)  # rate `amount` is integer minor units; GET on rate paths 405s

OPERATIONS = (
    PROJECTS_CREATE,
    PROJECTS_CREATE_FROM_TEMPLATE,
    PROJECTS_DELETE,
    PROJECTS_GET,
    PROJECTS_LIST,
    PROJECTS_SET_MEMBERS,
    PROJECTS_UPDATE,
    PROJECTS_UPDATE_ESTIMATE,
    PROJECTS_UPDATE_MEMBERSHIPS,
    PROJECTS_UPDATE_TEMPLATE,
    PROJECTS_UPDATE_USER_COST_RATE,
    PROJECTS_UPDATE_USER_HOURLY_RATE,
)
