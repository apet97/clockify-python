"""Operation records for the `tasks` resource.

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

TASKS_CREATE = Operation(
    operation_id="addTaskOnProject",
    resource="tasks",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/tasks",
    path_parameters=("workspaceId", "projectId"),
    query_parameters=(QueryParameter("contains_assignee", "contains-assignee"),),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TASKS_DELETE = Operation(
    operation_id="deleteTaskFromProject",
    resource="tasks",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}",
    path_parameters=("workspaceId", "projectId", "taskId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
        lifecycle="done_before_delete",
    ),
)

TASKS_GET = Operation(
    operation_id="getTaskById",
    resource="tasks",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}",
    path_parameters=("workspaceId", "projectId", "taskId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TASKS_LIST = Operation(
    operation_id="findTasksOnProject",
    resource="tasks",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/tasks",
    path_parameters=("workspaceId", "projectId"),
    query_parameters=(
        QueryParameter("name", "name"),
        QueryParameter("strict_name_search", "strict-name-search"),
        QueryParameter("is_active", "is-active"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("sort_column", "sort-column"),
        QueryParameter("sort_order", "sort-order"),
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

TASKS_UPDATE = Operation(
    operation_id="updateTaskOnProject",
    resource="tasks",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}",
    path_parameters=("workspaceId", "projectId", "taskId"),
    query_parameters=(
        QueryParameter("contains_assignee", "contains-assignee"),
        QueryParameter("membership_status", "membership-status"),
    ),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.FULL_REPLACE_PROVEN,
    ),
)

TASKS_UPDATE_BILLABLE_RATE = Operation(
    operation_id="updateTaskBillableRate",
    resource="tasks",
    sdk_method="update_billable_rate",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/hourly-rate",
    path_parameters=("workspaceId", "projectId", "taskId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)  # rate `amount` is integer minor units (cents); GET on a rate path 405s

TASKS_UPDATE_COST_RATE = Operation(
    operation_id="updateTaskCostRate",
    resource="tasks",
    sdk_method="update_cost_rate",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/cost-rate",
    path_parameters=("workspaceId", "projectId", "taskId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)  # rate `amount` is integer minor units (cents); GET on a rate path 405s

OPERATIONS = (
    TASKS_CREATE,
    TASKS_DELETE,
    TASKS_GET,
    TASKS_LIST,
    TASKS_UPDATE,
    TASKS_UPDATE_BILLABLE_RATE,
    TASKS_UPDATE_COST_RATE,
)
