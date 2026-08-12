"""Audit log resource: search over the dedicated audit-log service."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import AuditLogRequest, AuditLogResponse
from clockify.operations.audit_log import AUDIT_LOG_SEARCH
from clockify.resources._base import ResourceBase

_AUDIT_LOG_RESPONSE = TypeAdapter(AuditLogResponse)


class AuditLogResource(ResourceBase):
    async def search(
        self,
        body: "AuditLogRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> AuditLogResponse:
        """Non-mutating POST search filter; actions is a closed enum, invented values fail."""
        validated = self._coerce(body, AuditLogRequest)
        response = await self._call(
            AUDIT_LOG_SEARCH,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(AUDIT_LOG_SEARCH, response, _AUDIT_LOG_RESPONSE)
