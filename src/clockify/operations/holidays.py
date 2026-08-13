"""Operation records for the `holidays` resource.

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

HOLIDAYS_CREATE = Operation(
    operation_id="createHoliday",
    resource="holidays",
    sdk_method="create",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/holidays",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)  # assignment is a {contains,ids,status} filter under users/userGroups on the wire

HOLIDAYS_DELETE = Operation(
    operation_id="deleteHoliday",
    resource="holidays",
    sdk_method="delete",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/holidays/{holidayId}",
    path_parameters=("workspaceId", "holidayId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,  # 200 returns HolidayDetailsDto
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

HOLIDAYS_LIST = Operation(
    operation_id="getWorkspaceHolidays",
    resource="holidays",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/holidays",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("assigned_to", "assigned-to"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=None,  # bare array
        last_page_header=True,  # holidays is in the audited Last-Page stamped set
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

HOLIDAYS_LIST_IN_PERIOD = Operation(
    operation_id="getWorkspaceHolidaysInPeriod",
    resource="holidays",
    sdk_method="list_in_period",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/holidays/in-period",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("assigned_to", "assigned-to", required=True),
        QueryParameter("start", "start", required=True),
        QueryParameter("end", "end", required=True),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

HOLIDAYS_UPDATE = Operation(
    operation_id="updateHoliday",
    resource="holidays",
    sdk_method="update",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/holidays/{holidayId}",
    path_parameters=("workspaceId", "holidayId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.FULL_REPLACE_PROVEN,
    ),
)  # replaces document; omitted fields 400; no single-GET route (list-scan first)

OPERATIONS = (
    HOLIDAYS_CREATE,
    HOLIDAYS_DELETE,
    HOLIDAYS_LIST,
    HOLIDAYS_LIST_IN_PERIOD,
    HOLIDAYS_UPDATE,
)
