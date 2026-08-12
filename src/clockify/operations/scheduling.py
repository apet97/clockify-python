"""Operation records for the `scheduling` resource.

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

SCHEDULING_CHANGE_RECURRING_PERIOD = Operation(
    operation_id="changeRecurringPeriod",
    resource="scheduling",
    sdk_method="change_recurring_period",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/series/{assignmentId}",
    path_parameters=("workspaceId", "assignmentId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)  # response is a bare array of SchedulingAssignment

SCHEDULING_COPY_ASSIGNMENT = Operation(
    operation_id="copyScheduledAssignment",
    resource="scheduling",
    sdk_method="copy_assignment",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/{assignmentId}/copy",
    path_parameters=("workspaceId", "assignmentId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

SCHEDULING_CREATE_RECURRING = Operation(
    operation_id="createRecurringAssignment",
    resource="scheduling",
    sdk_method="create_recurring",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/recurring",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # 201 bare array of SchedulingAssignment; created-entity id is element [0]

SCHEDULING_DELETE_RECURRING = Operation(
    operation_id="deleteRecurringAssignment",
    resource="scheduling",
    sdk_method="delete_recurring",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/recurring/{assignmentId}",
    path_parameters=("workspaceId", "assignmentId"),
    query_parameters=(QueryParameter("series_update_option", "seriesUpdateOption"),),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

SCHEDULING_GET_FILTERED_USER_CAPACITY = Operation(
    operation_id="getUsersCapacityTotals",
    resource="scheduling",
    sdk_method="get_filtered_user_capacity",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/user-filter/totals",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

SCHEDULING_GET_PROJECT_TOTALS = Operation(
    operation_id="getScheduledAssignmentsOnProject",
    resource="scheduling",
    sdk_method="get_project_totals",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/projects/totals/{projectId}",
    path_parameters=("workspaceId", "projectId"),
    query_parameters=(
        QueryParameter("start", "start"),
        QueryParameter("end", "end"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # start and end are required by live Clockify; the GET 400s without them

SCHEDULING_GET_USER_CAPACITY = Operation(
    operation_id="getUserCapacityTotal",
    resource="scheduling",
    sdk_method="get_user_capacity",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/users/{userId}/totals",
    path_parameters=("workspaceId", "userId"),
    query_parameters=(
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
        QueryParameter("start", "start"),
        QueryParameter("end", "end"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=("totalHoursPerDay",),
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

SCHEDULING_LIST_ASSIGNMENTS = Operation(
    operation_id="getAllSchedulingAssignments",
    resource="scheduling",
    sdk_method="list_assignments",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/all",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("name", "name"),
        QueryParameter("start", "start"),
        QueryParameter("end", "end"),
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

SCHEDULING_LIST_PROJECT_TOTALS = Operation(
    operation_id="getScheduledAssignmentsPerProject",
    resource="scheduling",
    sdk_method="list_project_totals",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/projects/totals",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # body requires start+end and reads only camel pageSize; kebab page-size is ignored

SCHEDULING_PUBLISH_ASSIGNMENTS = Operation(
    operation_id="publishAssignments",
    resource="scheduling",
    sdk_method="publish_assignments",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/publish",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)  # range-scoped multi-entity publish; 200 with empty body

SCHEDULING_UPDATE_RECURRING = Operation(
    operation_id="updateRecurringAssignment",
    resource="scheduling",
    sdk_method="update_recurring",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/scheduling/assignments/recurring/{assignmentId}",
    path_parameters=("workspaceId", "assignmentId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.PATCH,
    ),
)

OPERATIONS = (
    SCHEDULING_CHANGE_RECURRING_PERIOD,
    SCHEDULING_COPY_ASSIGNMENT,
    SCHEDULING_CREATE_RECURRING,
    SCHEDULING_DELETE_RECURRING,
    SCHEDULING_GET_FILTERED_USER_CAPACITY,
    SCHEDULING_GET_PROJECT_TOTALS,
    SCHEDULING_GET_USER_CAPACITY,
    SCHEDULING_LIST_ASSIGNMENTS,
    SCHEDULING_LIST_PROJECT_TOTALS,
    SCHEDULING_PUBLISH_ASSIGNMENTS,
    SCHEDULING_UPDATE_RECURRING,
)
