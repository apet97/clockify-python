"""Concrete shared plumbing for resource objects.

Only workspace resolution, request-model coercion, and response adaptation live
here. There is deliberately no generic CRUD layer.
"""

from collections.abc import Mapping
from typing import Any, TypeVar

import pydantic
from pydantic import BaseModel, TypeAdapter

from clockify._transport.executor import HttpExecutor, ReadOnlyExecutor
from clockify.errors import ClockifyConfigurationError, ClockifyResponseValidationError
from clockify.files import Upload
from clockify.operations.model import Operation
from clockify.response import ClockifyResponse

ModelT = TypeVar("ModelT", bound=BaseModel)


class ResourceBase:
    def __init__(
        self, executor: "HttpExecutor | ReadOnlyExecutor", default_workspace_id: str | None
    ) -> None:
        self._executor = executor
        self._default_workspace_id = default_workspace_id

    def _workspace(self, override: str | None) -> str:
        workspace_id = override or self._default_workspace_id
        if not workspace_id:
            raise ClockifyConfigurationError(
                "workspace_id is required: pass it to the call or set it on ClockifyClient"
            )
        return workspace_id

    async def _call(
        self,
        operation: Operation,
        *,
        path: dict[str, str],
        query: dict[str, Any] | None = None,
        body: Any = None,
        files: dict[str, Upload] | None = None,
    ) -> ClockifyResponse[Any]:
        return await self._executor.execute(
            operation, path_args=path, query=query, body=body, files=files
        )

    @staticmethod
    def _coerce(body: "ModelT | Mapping[str, Any]", model: type[ModelT]) -> ModelT:
        """Validate a mapping into the operation's request model; models pass through."""
        if isinstance(body, model):
            return body
        if isinstance(body, Mapping):
            return model.model_validate(dict(body))
        raise ClockifyConfigurationError(
            f"body must be {model.__name__} or a mapping, not {type(body).__name__}"
        )

    @staticmethod
    def _adapt(operation: Operation, response: ClockifyResponse[Any], adapter: Any) -> Any:
        """Validate a decoded JSON payload through a model class or TypeAdapter."""
        if response.data is None:
            return None
        try:
            if isinstance(adapter, TypeAdapter):
                return adapter.validate_python(response.data)
            return adapter.model_validate(response.data)
        except pydantic.ValidationError as exc:
            raise ClockifyResponseValidationError(
                f"{operation.operation_id}: response did not match the declared model: {exc}",
                operation_id=operation.operation_id,
                request_id=response.request_id,
            ) from exc
