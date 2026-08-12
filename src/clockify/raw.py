"""Bounded raw escape hatch: call any registered operation without model adaptation.

Only registered operation IDs are accepted; there is no way to send an
arbitrary URL. All auth, host-validation, retry, and error behavior is the
same executor boundary the typed methods use.
"""

from typing import Any

import httpx

from clockify._transport.executor import HttpExecutor, ReadOnlyExecutor
from clockify.errors import ClockifyConfigurationError
from clockify.files import Upload
from clockify.operations.registry import BY_ID
from clockify.response import ClockifyResponse


class RawOperations:
    def __init__(self, executor: "HttpExecutor | ReadOnlyExecutor") -> None:
        self._executor = executor

    async def call(
        self,
        operation_id: str,
        *,
        path: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        body: Any = None,
        files: dict[str, Upload] | None = None,
        headers: dict[str, str] | None = None,
        timeout: httpx.Timeout | None = None,
    ) -> ClockifyResponse[Any]:
        operation = BY_ID.get(operation_id)
        if operation is None:
            raise ClockifyConfigurationError(f"unknown operation_id {operation_id!r}")
        return await self._executor.execute(
            operation,
            path_args=path or {},
            query=query,
            body=body,
            files=files,
            headers=headers,
            timeout=timeout,
        )
