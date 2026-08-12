"""Structured result envelope every raw read tool returns."""

from typing import Any

from pydantic import BaseModel

from clockify.response import ClockifyResponse


class ReadResult(BaseModel):
    """Uniform tool payload: data plus the metadata agents need for follow-ups."""

    data: Any
    operation_id: str
    request_id: str | None = None
    last_page: bool | None = None
    warnings: list[str] = []


def read_result(
    response: ClockifyResponse[Any], data: Any, *, warnings: list[str] | None = None
) -> ReadResult:
    def to_plain(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(by_alias=True)
        if isinstance(value, list):
            return [to_plain(item) for item in value]
        return value

    return ReadResult(
        data=to_plain(data),
        operation_id=response.operation_id,
        request_id=response.request_id,
        last_page=response.last_page,
        warnings=warnings or [],
    )
