"""Time-off balances resource: explicit methods over the balance operations."""

from collections.abc import Mapping
from typing import Any

from clockify.models import BalanceListResponse, UpdateBalanceRequest
from clockify.operations.time_off_balances import (
    TIME_OFF_BALANCES_LIST_FOR_POLICY,
    TIME_OFF_BALANCES_LIST_FOR_USER,
    TIME_OFF_BALANCES_UPDATE_FOR_POLICY,
)
from clockify.resources._base import ResourceBase


class TimeOffBalancesResource(ResourceBase):
    async def list_for_policy(
        self,
        policy_id: str,
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort: str | None = None,
        sort_order: str | None = None,
    ) -> BalanceListResponse:
        """Envelope response: items are under `balances`."""
        response = await self._call(
            TIME_OFF_BALANCES_LIST_FOR_POLICY,
            path={"workspaceId": self._workspace(workspace_id), "policyId": policy_id},
            query={
                "page": page,
                "page_size": page_size,
                "sort": sort,
                "sort_order": sort_order,
            },
        )
        return self._adapt(TIME_OFF_BALANCES_LIST_FOR_POLICY, response, BalanceListResponse)

    async def list_for_user(
        self,
        user_id: str,
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort: str | None = None,
        sort_order: str | None = None,
    ) -> BalanceListResponse:
        """Envelope response: items are under `balances`."""
        response = await self._call(
            TIME_OFF_BALANCES_LIST_FOR_USER,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            query={
                "page": page,
                "page_size": page_size,
                "sort": sort,
                "sort_order": sort_order,
            },
        )
        return self._adapt(TIME_OFF_BALANCES_LIST_FOR_USER, response, BalanceListResponse)

    async def update_for_policy(
        self,
        policy_id: str,
        body: "UpdateBalanceRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> None:
        validated = self._coerce(body, UpdateBalanceRequest)
        await self._call(
            TIME_OFF_BALANCES_UPDATE_FOR_POLICY,
            path={"workspaceId": self._workspace(workspace_id), "policyId": policy_id},
            body=validated,
        )
        return None
