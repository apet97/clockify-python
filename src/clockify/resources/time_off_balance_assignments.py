"""Time-off balance assignments resource: explicit methods over the operations."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    BalanceAssignmentV1Dto,
    CreateBalanceAssignmentV1Request,
    DeleteBalanceAssignmentV1Request,
    UpdateBalanceAssignmentV1Request,
)
from clockify.operations.time_off_balance_assignments import (
    TIME_OFF_BALANCE_ASSIGNMENTS_CREATE,
    TIME_OFF_BALANCE_ASSIGNMENTS_DELETE,
    TIME_OFF_BALANCE_ASSIGNMENTS_GET_FOR_USER_AND_POLICY,
    TIME_OFF_BALANCE_ASSIGNMENTS_UPDATE,
)
from clockify.resources._base import ResourceBase

_ASSIGNMENT_LIST = TypeAdapter(list[BalanceAssignmentV1Dto])


class TimeOffBalanceAssignmentsResource(ResourceBase):
    async def create(
        self,
        body: "CreateBalanceAssignmentV1Request | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> None:
        """Additive, not idempotent: repeating adds `balance` to `accrued` again."""
        validated = self._coerce(body, CreateBalanceAssignmentV1Request)
        await self._call(
            TIME_OFF_BALANCE_ASSIGNMENTS_CREATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return None

    async def delete(
        self,
        balance_assignment_id: str,
        user_id: str,
        policy_id: str,
        body: "DeleteBalanceAssignmentV1Request | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> None:
        """DELETE with a required JSON body (`note`)."""
        validated = self._coerce(body, DeleteBalanceAssignmentV1Request)
        await self._call(
            TIME_OFF_BALANCE_ASSIGNMENTS_DELETE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "balanceAssignmentId": balance_assignment_id,
                "userId": user_id,
                "policyId": policy_id,
            },
            body=validated,
        )
        return None

    async def get_for_user_and_policy(
        self, user_id: str, policy_id: str, *, workspace_id: str | None = None
    ) -> list[BalanceAssignmentV1Dto]:
        response = await self._call(
            TIME_OFF_BALANCE_ASSIGNMENTS_GET_FOR_USER_AND_POLICY,
            path={
                "workspaceId": self._workspace(workspace_id),
                "userId": user_id,
                "policyId": policy_id,
            },
        )
        return self._adapt(
            TIME_OFF_BALANCE_ASSIGNMENTS_GET_FOR_USER_AND_POLICY, response, _ASSIGNMENT_LIST
        )

    async def update(
        self,
        balance_assignment_id: str,
        user_id: str,
        policy_id: str,
        body: "UpdateBalanceAssignmentV1Request | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> None:
        """`balanceChange` is applied as a delta, not a replacement value."""
        validated = self._coerce(body, UpdateBalanceAssignmentV1Request)
        await self._call(
            TIME_OFF_BALANCE_ASSIGNMENTS_UPDATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "balanceAssignmentId": balance_assignment_id,
                "userId": user_id,
                "policyId": policy_id,
            },
            body=validated,
        )
        return None
