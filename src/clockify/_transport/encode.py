"""Pure request compilation.

`compile_request` turns an operation plus caller arguments into the exact wire
request without touching the network. The MCP write gate later reuses this to
bind approved plans to the precise bytes that will be dispatched.
"""

from dataclasses import dataclass, field
from typing import Any, BinaryIO
from urllib.parse import quote

from pydantic import BaseModel

from clockify.errors import ClockifyConfigurationError
from clockify.files import Upload
from clockify.operations.model import Operation, RequestEncoding

MultipartFile = tuple[str, tuple[str, "bytes | BinaryIO", str]]


@dataclass(frozen=True, slots=True)
class CompiledRequest:
    method: str
    url: str
    params: tuple[tuple[str, str], ...] = ()
    json_body: Any = None
    form_data: tuple[tuple[str, str], ...] | None = None
    files: tuple[MultipartFile, ...] = ()
    headers: dict[str, str] = field(default_factory=dict)


def render_path(operation: Operation, path_args: dict[str, Any]) -> str:
    """Fill the path template; every declared parameter is required, extras rejected."""
    missing = set(operation.path_parameters) - set(path_args)
    if missing:
        raise ClockifyConfigurationError(
            f"{operation.operation_id}: missing path parameters {sorted(missing)}"
        )
    extra = set(path_args) - set(operation.path_parameters)
    if extra:
        raise ClockifyConfigurationError(
            f"{operation.operation_id}: unknown path parameters {sorted(extra)}"
        )
    rendered = operation.path
    for name, value in path_args.items():
        if not isinstance(value, str) or not value:
            raise ClockifyConfigurationError(
                f"{operation.operation_id}: path parameter {name!r} must be a non-empty string"
            )
        if value in (".", ".."):
            # httpx normalizes dot segments, which would retarget the request
            # within the same service (review finding F4).
            raise ClockifyConfigurationError(
                f"{operation.operation_id}: path parameter {name!r} must not be a dot segment"
            )
        rendered = rendered.replace("{" + name + "}", quote(value, safe=""))
    return rendered


def _scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def serialize_query(operation: Operation, query: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    """Map Python names to exact wire names; None means omitted."""
    known = {q.python_name: q for q in operation.query_parameters}
    unknown = set(query) - set(known)
    if unknown:
        raise ClockifyConfigurationError(
            f"{operation.operation_id}: unknown query parameters {sorted(unknown)}"
        )
    pairs: list[tuple[str, str]] = []
    for parameter in operation.query_parameters:
        value = query.get(parameter.python_name)
        if value is None:
            continue
        if isinstance(value, (list, tuple, set, frozenset)):
            items = [_scalar(v) for v in value]
            if parameter.explode:
                pairs.extend((parameter.wire_name, item) for item in items)
            else:
                pairs.append((parameter.wire_name, ",".join(items)))
        else:
            pairs.append((parameter.wire_name, _scalar(value)))
    return tuple(pairs)


def serialize_body(operation: Operation, body: Any) -> Any:
    if operation.request_encoding is RequestEncoding.NONE:
        if body is not None:
            raise ClockifyConfigurationError(
                f"{operation.operation_id}: operation takes no request body"
            )
        return None
    if body is None:
        return None
    if isinstance(body, BaseModel):
        # Aliases give exact wire keys; explicit None survives, unset is omitted.
        # Multipart bodies dump in python mode: their fields become scalar form
        # parts (json mode would crash on binary bytes before we can reject).
        if operation.request_encoding is RequestEncoding.MULTIPART:
            return body.model_dump(by_alias=True, exclude_unset=True)
        return body.model_dump(by_alias=True, exclude_unset=True, mode="json")
    if isinstance(body, (dict, list)):
        return body
    raise ClockifyConfigurationError(
        f"{operation.operation_id}: unsupported body type {type(body).__name__}"
    )


def serialize_files(
    operation: Operation, files: dict[str, Upload] | None
) -> tuple[MultipartFile, ...]:
    if operation.request_encoding is not RequestEncoding.MULTIPART:
        if files:
            raise ClockifyConfigurationError(
                f"{operation.operation_id}: operation does not accept files"
            )
        return ()
    if not files:
        return ()
    return tuple(
        (field_name, (upload.filename, upload.content, upload.content_type))
        for field_name, upload in files.items()
    )


def compile_request(
    operation: Operation,
    *,
    base_url: str,
    path_args: dict[str, str],
    query: dict[str, Any],
    body: Any,
    files: dict[str, Upload] | None,
    headers: dict[str, str],
) -> CompiledRequest:
    path = render_path(operation, path_args)
    params = serialize_query(operation, query)
    serialized_body = serialize_body(operation, body)
    file_parts = serialize_files(operation, files)

    if operation.request_encoding is RequestEncoding.MULTIPART:
        form: list[tuple[str, str]] = []
        if serialized_body:
            if not isinstance(serialized_body, dict):
                raise ClockifyConfigurationError(
                    f"{operation.operation_id}: multipart body must be a mapping"
                )
            for key, value in serialized_body.items():
                if value is None:
                    continue
                if isinstance(value, bytes):
                    raise ClockifyConfigurationError(
                        f"{operation.operation_id}: binary content must be sent"
                        f" via the file=Upload(...) parameter, not the body"
                        f" field {key!r}"
                    )
                # A list field becomes one repeated part per item (evidence:
                # updateExpense changeFields in the corrected spec / TS wrapper).
                if isinstance(value, (list, tuple)):
                    form.extend((key, _scalar(item)) for item in value)
                else:
                    form.append((key, _scalar(value)))
        return CompiledRequest(
            method=operation.http_method,
            url=base_url + path,
            params=params,
            form_data=tuple(form) or None,
            files=file_parts,
            headers=headers,
        )

    return CompiledRequest(
        method=operation.http_method,
        url=base_url + path,
        params=params,
        json_body=serialized_body,
        headers=headers,
    )
