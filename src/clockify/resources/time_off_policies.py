"""Time-off policies resource: explicit methods over the time-off policy operations."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    CreateTimeOffPolicyRequest,
    Policy,
    PolicyStatusChangeRequest,
    UpdateTimeOffPolicyRequest,
)
from clockify.operations.time_off_policies import (
    TIME_OFF_POLICIES_CREATE,
    TIME_OFF_POLICIES_DELETE,
    TIME_OFF_POLICIES_GET,
    TIME_OFF_POLICIES_LIST,
    TIME_OFF_POLICIES_UPDATE,
    TIME_OFF_POLICIES_UPDATE_STATUS,
)
from clockify.resources._base import ResourceBase

_POLICY_LIST = TypeAdapter(list[Policy])


class TimeOffPoliciesResource(ResourceBase):
    async def create(
        self,
        body: "CreateTimeOffPolicyRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Policy:
        """`approve` is required despite spec optionality; omitting it returns code 501."""
        validated = self._coerce(body, CreateTimeOffPolicyRequest)
        response = await self._call(
            TIME_OFF_POLICIES_CREATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(TIME_OFF_POLICIES_CREATE, response, Policy)

    async def delete(self, policy_id: str, *, workspace_id: str | None = None) -> None:
        await self._call(
            TIME_OFF_POLICIES_DELETE,
            path={"workspaceId": self._workspace(workspace_id), "policyId": policy_id},
        )
        return None

    async def get(self, policy_id: str, *, workspace_id: str | None = None) -> Policy:
        response = await self._call(
            TIME_OFF_POLICIES_GET,
            path={"workspaceId": self._workspace(workspace_id), "policyId": policy_id},
        )
        return self._adapt(TIME_OFF_POLICIES_GET, response, Policy)

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        name: str | None = None,
        status: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
    ) -> list[Policy]:
        response = await self._call(
            TIME_OFF_POLICIES_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "page": page,
                "page_size": page_size,
                "name": name,
                "status": status,
                "sort_column": sort_column,
                "sort_order": sort_order,
            },
        )
        return self._adapt(TIME_OFF_POLICIES_LIST, response, _POLICY_LIST)

    async def update(
        self,
        policy_id: str,
        body: "UpdateTimeOffPolicyRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Policy:
        """Full replacement: carry forward every policy field (GET-then-PUT);
        `users`/`userGroups` go up as {contains,ids,status:"ACTIVE"} filters."""
        validated = self._coerce(body, UpdateTimeOffPolicyRequest)
        response = await self._call(
            TIME_OFF_POLICIES_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "policyId": policy_id},
            body=validated,
        )
        return self._adapt(TIME_OFF_POLICIES_UPDATE, response, Policy)

    async def update_status(
        self,
        policy_id: str,
        body: "PolicyStatusChangeRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Policy:
        validated = self._coerce(body, PolicyStatusChangeRequest)
        response = await self._call(
            TIME_OFF_POLICIES_UPDATE_STATUS,
            path={"workspaceId": self._workspace(workspace_id), "policyId": policy_id},
            body=validated,
        )
        return self._adapt(TIME_OFF_POLICIES_UPDATE_STATUS, response, Policy)
