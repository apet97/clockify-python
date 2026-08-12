"""Operation records for the `files` resource.

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

FILES_UPLOAD_IMAGE = Operation(
    operation_id="uploadImage",
    resource="files",
    sdk_method="upload_image",
    http_method="POST",
    service=Service.REGULAR,
    path="/file/image",
    path_parameters=(),
    request_encoding=RequestEncoding.MULTIPART,  # single required `file` part (binary)
    response_kind=ResponseKind.JSON,
    semantics=OperationSemantics(
        mutates=True,
        effect=MutationEffect.CREATE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

OPERATIONS = (FILES_UPLOAD_IMAGE,)
