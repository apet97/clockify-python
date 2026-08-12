"""Workspaces resource: explicit methods over the workspace operations."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    CreateWorkspaceRequest,
    UpdateCostRateRequest,
    UpdateWorkspaceBillableRateRequest,
    Workspace,
)
from clockify.operations.workspaces import (
    WORKSPACES_CREATE,
    WORKSPACES_GET,
    WORKSPACES_LIST,
    WORKSPACES_UPDATE_BILLABLE_RATE,
    WORKSPACES_UPDATE_COST_RATE,
)
from clockify.resources._base import ResourceBase

_WORKSPACE_LIST = TypeAdapter(list[Workspace])


class WorkspacesResource(ResourceBase):
    async def create(self, body: "CreateWorkspaceRequest | Mapping[str, Any]") -> Workspace:
        validated = self._coerce(body, CreateWorkspaceRequest)
        response = await self._call(WORKSPACES_CREATE, path={}, body=validated)
        return self._adapt(WORKSPACES_CREATE, response, Workspace)

    async def get(self, *, workspace_id: str | None = None) -> Workspace:
        response = await self._call(
            WORKSPACES_GET, path={"workspaceId": self._workspace(workspace_id)}
        )
        return self._adapt(WORKSPACES_GET, response, Workspace)

    async def list(self, *, roles: list[str] | None = None) -> list[Workspace]:
        """No server-side paging: the full collection returns; `roles` is a repeated key."""
        response = await self._call(WORKSPACES_LIST, path={}, query={"roles": roles})
        return self._adapt(WORKSPACES_LIST, response, _WORKSPACE_LIST)

    async def update_billable_rate(
        self,
        body: "UpdateWorkspaceBillableRateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Workspace:
        """`amount` is a raw integer in minor units; no currency scaling."""
        validated = self._coerce(body, UpdateWorkspaceBillableRateRequest)
        response = await self._call(
            WORKSPACES_UPDATE_BILLABLE_RATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(WORKSPACES_UPDATE_BILLABLE_RATE, response, Workspace)

    async def update_cost_rate(
        self,
        body: "UpdateCostRateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Workspace:
        """`amount` is a raw integer in minor units; no currency scaling."""
        validated = self._coerce(body, UpdateCostRateRequest)
        response = await self._call(
            WORKSPACES_UPDATE_COST_RATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(WORKSPACES_UPDATE_COST_RATE, response, Workspace)
