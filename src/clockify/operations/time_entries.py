"""Operation records for the `time_entries` resource.

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

TIME_ENTRIES_BULK_UPDATE_FOR_USER = Operation(
    operation_id="putWorkspacesWorkspaceIdUserUserIdTimeEntries",
    resource="time_entries",
    sdk_method="bulk_update_for_user",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user/{userId}/time-entries",
    path_parameters=("workspaceId", "userId"),
    query_parameters=(QueryParameter("hydrated", "hydrated"),),
    request_encoding=RequestEncoding.JSON,  # body is a bare JSON array of BulkEditTimeEntryRequest
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.BULK,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

TIME_ENTRIES_CREATE = Operation(
    operation_id="postWorkspacesWorkspaceIdTimeEntries",
    resource="time_entries",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-entries",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # custom fields write key is `customFields`; sending `customFieldValues` 201s but drops the value

TIME_ENTRIES_CREATE_FOR_USER = Operation(
    operation_id="postWorkspacesWorkspaceIdUserUserIdTimeEntries",
    resource="time_entries",
    sdk_method="create_for_user",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user/{userId}/time-entries",
    path_parameters=("workspaceId", "userId"),
    query_parameters=(QueryParameter("from_entry", "from-entry"),),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_ENTRIES_DELETE = Operation(
    operation_id="deleteWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
    resource="time_entries",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-entries/{timeEntryId}",
    path_parameters=("workspaceId", "timeEntryId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_ENTRIES_DELETE_ALL_FOR_USER = Operation(
    operation_id="deleteMany",
    resource="time_entries",
    sdk_method="delete_all_for_user",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user/{userId}/time-entries",
    path_parameters=("workspaceId", "userId"),
    query_parameters=(QueryParameter("time_entry_ids", "time-entry-ids", required=True),),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_ENTRIES_DUPLICATE = Operation(
    operation_id="postWorkspacesWorkspaceIdUserUserIdTimeEntriesTimeEntryIdDuplicate",
    resource="time_entries",
    sdk_method="duplicate",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user/{userId}/time-entries/{timeEntryId}/duplicate",
    path_parameters=("workspaceId", "userId", "timeEntryId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_ENTRIES_GET = Operation(
    operation_id="getWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
    resource="time_entries",
    sdk_method="get",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-entries/{timeEntryId}",
    path_parameters=("workspaceId", "timeEntryId"),
    query_parameters=(
        QueryParameter("hydrated", "hydrated"),
        QueryParameter("consider_duration_format", "consider-duration-format"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_ENTRIES_GET_MANY = Operation(
    operation_id="getMultipleTimeEntries",
    resource="time_entries",
    sdk_method="get_many",
    http_method="POST",  # non-mutating POST: batch read of time entries by id
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-entries/batch",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_ENTRIES_LIST_FOR_USER = Operation(
    operation_id="getWorkspacesWorkspaceIdUserUserIdTimeEntries",
    resource="time_entries",
    sdk_method="list_for_user",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user/{userId}/time-entries",
    path_parameters=("workspaceId", "userId"),
    query_parameters=(
        QueryParameter("description", "description"),
        QueryParameter("start", "start"),
        QueryParameter("end", "end"),
        QueryParameter("project", "project"),
        QueryParameter("task", "task"),
        QueryParameter("tags", "tags"),
        QueryParameter("project_required", "project-required"),
        QueryParameter("task_required", "task-required"),
        QueryParameter("hydrated", "hydrated"),
        QueryParameter("in_progress", "in-progress"),
        QueryParameter("get_week_before", "get-week-before"),
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
)  # start/end window is re-read as wall clock in the account's timezone

TIME_ENTRIES_LIST_IN_PROGRESS = Operation(
    operation_id="getWorkspacesWorkspaceIdTimeEntriesStatusInProgress",
    resource="time_entries",
    sdk_method="list_in_progress",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-entries/status/in-progress",
    path_parameters=("workspaceId",),
    query_parameters=(
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

TIME_ENTRIES_MARK_INVOICED = Operation(
    operation_id="patchWorkspacesWorkspaceIdTimeEntriesInvoiced",
    resource="time_entries",
    sdk_method="mark_invoiced",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-entries/invoiced",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.NONE,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.TRANSITION,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

TIME_ENTRIES_STOP_TIMER_FOR_USER = Operation(
    operation_id="patchWorkspacesWorkspaceIdUserUserIdTimeEntries",
    resource="time_entries",
    sdk_method="stop_timer_for_user",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/user/{userId}/time-entries",
    path_parameters=("workspaceId", "userId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.PATCH,
    ),
)

TIME_ENTRIES_UPDATE = Operation(
    operation_id="putWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
    resource="time_entries",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/time-entries/{timeEntryId}",
    path_parameters=("workspaceId", "timeEntryId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

OPERATIONS = (
    TIME_ENTRIES_BULK_UPDATE_FOR_USER,
    TIME_ENTRIES_CREATE,
    TIME_ENTRIES_CREATE_FOR_USER,
    TIME_ENTRIES_DELETE,
    TIME_ENTRIES_DELETE_ALL_FOR_USER,
    TIME_ENTRIES_DUPLICATE,
    TIME_ENTRIES_GET,
    TIME_ENTRIES_GET_MANY,
    TIME_ENTRIES_LIST_FOR_USER,
    TIME_ENTRIES_LIST_IN_PROGRESS,
    TIME_ENTRIES_MARK_INVOICED,
    TIME_ENTRIES_STOP_TIMER_FOR_USER,
    TIME_ENTRIES_UPDATE,
)
