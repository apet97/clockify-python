"""Concrete shared plumbing for resource objects.

Only workspace resolution, request-model coercion, and response adaptation live
here. There is deliberately no generic CRUD layer.
"""

from collections.abc import Mapping, Sequence
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
        """Validate a request model and reject unknown fields at every depth."""
        if isinstance(body, model):
            validated = body
        elif isinstance(body, Mapping):
            validated = model.model_validate(dict(body))
        else:
            raise ClockifyConfigurationError(
                f"body must be {model.__name__} or a mapping, not {type(body).__name__}"
            )
        extra_paths, extra_count = ResourceBase._extra_summary(validated)
        if extra_count:
            remainder = extra_count - len(extra_paths)
            suffix = f"; {remainder} more" if remainder else ""
            message = f"body contains unknown fields: {', '.join(extra_paths)}{suffix}"
            raise ClockifyConfigurationError(message[:500])
        return validated

    @staticmethod
    def _extra_summary(value: Any) -> tuple[list[str], int]:
        """Return at most ten stable extra-field paths and the complete count."""
        paths: list[str] = []
        count = 0

        def collect(item: Any, path: str = "") -> None:
            nonlocal count
            if isinstance(item, BaseModel):
                for name in sorted(item.model_extra or {}):
                    count += 1
                    if len(paths) < 10:
                        paths.append(f"{path}.{name}" if path else name)
                for field_name in item.__class__.model_fields:
                    field_path = f"{path}.{field_name}" if path else field_name
                    collect(getattr(item, field_name), field_path)
            elif isinstance(item, Mapping):
                for key, nested in item.items():
                    item_path = f"{path}.{key}" if path else str(key)
                    collect(nested, item_path)
            elif isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
                for index, nested in enumerate(item):
                    collect(nested, f"{path}[{index}]")

        collect(value)
        return paths, count

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
            error_count = exc.error_count()
        raise ClockifyResponseValidationError(
            f"{operation.operation_id}: response validation failed with {error_count} error(s)",
            operation_id=operation.operation_id,
            request_id=response.request_id,
        )
