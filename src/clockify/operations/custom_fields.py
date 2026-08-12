"""Operation records for the `custom_fields` resource.

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

CUSTOM_FIELDS_CREATE_FOR_WORKSPACE = Operation(
    operation_id="createWorkspaceCustomField",
    resource="custom_fields",
    sdk_method="create_for_workspace",
    http_method="POST",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/custom-fields",
    path_parameters=("workspaceId",),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

CUSTOM_FIELDS_DELETE_FOR_WORKSPACE = Operation(
    operation_id="deleteWorkspaceCustomField",
    resource="custom_fields",
    sdk_method="delete_for_workspace",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/custom-fields/{customFieldId}",
    path_parameters=("workspaceId", "customFieldId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.NONE,  # 204, no body
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

CUSTOM_FIELDS_LIST_FOR_PROJECT = Operation(
    operation_id="listProjectCustomFields",
    resource="custom_fields",
    sdk_method="list_for_project",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/custom-fields",
    path_parameters=("workspaceId", "projectId"),
    query_parameters=(
        QueryParameter("status", "status"),
        QueryParameter("entity_type", "entity-type"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=None,
        last_page_header=True,  # in the audited LAST_PAGE_HEADER_OPS stamped set
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

CUSTOM_FIELDS_LIST_FOR_WORKSPACE = Operation(
    operation_id="listWorkspaceCustomFields",
    resource="custom_fields",
    sdk_method="list_for_workspace",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/custom-fields",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("name", "name"),
        QueryParameter("status", "status"),
        QueryParameter("entity_type", "entity-type"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=None,
        last_page_header=True,  # in the audited LAST_PAGE_HEADER_OPS stamped set
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

CUSTOM_FIELDS_REMOVE_FROM_PROJECT = Operation(
    operation_id="removeProjectCustomField",
    resource="custom_fields",
    sdk_method="remove_from_project",
    http_method="DELETE",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/custom-fields/{customFieldId}",
    path_parameters=("workspaceId", "projectId", "customFieldId"),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.DELETE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

CUSTOM_FIELDS_UPDATE_FOR_PROJECT = Operation(
    operation_id="updateProjectCustomField",
    resource="custom_fields",
    sdk_method="update_for_project",
    http_method="PATCH",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/projects/{projectId}/custom-fields/{customFieldId}",
    path_parameters=("workspaceId", "projectId", "customFieldId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.PATCH,
        replacement=ReplacementSemantics.PATCH,
    ),
)

CUSTOM_FIELDS_UPDATE_FOR_WORKSPACE = Operation(
    operation_id="updateWorkspaceCustomField",
    resource="custom_fields",
    sdk_method="update_for_workspace",
    http_method="PUT",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/custom-fields/{customFieldId}",
    path_parameters=("workspaceId", "customFieldId"),
    request_encoding=RequestEncoding.JSON,
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.REPLACE,
        replacement=ReplacementSemantics.UNKNOWN_CONSERVATIVE,
    ),
)

OPERATIONS = (
    CUSTOM_FIELDS_CREATE_FOR_WORKSPACE,
    CUSTOM_FIELDS_DELETE_FOR_WORKSPACE,
    CUSTOM_FIELDS_LIST_FOR_PROJECT,
    CUSTOM_FIELDS_LIST_FOR_WORKSPACE,
    CUSTOM_FIELDS_REMOVE_FROM_PROJECT,
    CUSTOM_FIELDS_UPDATE_FOR_PROJECT,
    CUSTOM_FIELDS_UPDATE_FOR_WORKSPACE,
)
