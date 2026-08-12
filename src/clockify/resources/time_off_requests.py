"""Time-off requests resource: explicit methods over the time-off request operations."""

from collections.abc import Mapping
from typing import Any

from clockify.models import (
    ChangeTimeOffRequestStatusRequest,
    CreateTimeOffRequest,
    TimeOffRequestDto,
    TimeOffRequestFullV1Dto,
    TimeOffRequestSearchRequest,
    TimeOffRequestsResponse,
)
from clockify.operations.time_off_requests import (
    TIME_OFF_REQUESTS_LIST,
    TIME_OFF_REQUESTS_SUBMIT,
    TIME_OFF_REQUESTS_SUBMIT_FOR_USER,
    TIME_OFF_REQUESTS_UPDATE_STATUS,
    TIME_OFF_REQUESTS_WITHDRAW,
)
from clockify.resources._base import ResourceBase


class TimeOffRequestsResource(ResourceBase):
    async def list(
        self,
        body: "TimeOffRequestSearchRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> TimeOffRequestsResponse:
        """Non-mutating search POST; items arrive under the `requests` envelope key."""
        validated = self._coerce(body, TimeOffRequestSearchRequest)
        response = await self._call(
            TIME_OFF_REQUESTS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(TIME_OFF_REQUESTS_LIST, response, TimeOffRequestsResponse)

    async def submit(
        self,
        policy_id: str,
        body: "CreateTimeOffRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> TimeOffRequestFullV1Dto:
        """Period shape is policy-unit-dependent: DAYS wants {start,days}; HOURS wants
        {start,end} RFC3339 without milliseconds."""
        validated = self._coerce(body, CreateTimeOffRequest)
        response = await self._call(
            TIME_OFF_REQUESTS_SUBMIT,
            path={"workspaceId": self._workspace(workspace_id), "policyId": policy_id},
            body=validated,
        )
        return self._adapt(TIME_OFF_REQUESTS_SUBMIT, response, TimeOffRequestFullV1Dto)

    async def submit_for_user(
        self,
        policy_id: str,
        user_id: str,
        body: "CreateTimeOffRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> TimeOffRequestFullV1Dto:
        """Same policy-unit-dependent period shape as `submit`."""
        validated = self._coerce(body, CreateTimeOffRequest)
        response = await self._call(
            TIME_OFF_REQUESTS_SUBMIT_FOR_USER,
            path={
                "workspaceId": self._workspace(workspace_id),
                "policyId": policy_id,
                "userId": user_id,
            },
            body=validated,
        )
        return self._adapt(TIME_OFF_REQUESTS_SUBMIT_FOR_USER, response, TimeOffRequestFullV1Dto)

    async def update_status(
        self,
        policy_id: str,
        request_id: str,
        body: "ChangeTimeOffRequestStatusRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> TimeOffRequestDto:
        """Wire field is `status`; only APPROVED / REJECTED are valid targets."""
        validated = self._coerce(body, ChangeTimeOffRequestStatusRequest)
        response = await self._call(
            TIME_OFF_REQUESTS_UPDATE_STATUS,
            path={
                "workspaceId": self._workspace(workspace_id),
                "policyId": policy_id,
                "requestId": request_id,
            },
            body=validated,
        )
        return self._adapt(TIME_OFF_REQUESTS_UPDATE_STATUS, response, TimeOffRequestDto)

    async def withdraw(
        self, policy_id: str, request_id: str, *, workspace_id: str | None = None
    ) -> TimeOffRequestDto:
        """Valid only while the request is PENDING; APPROVED/REJECTED requests
        have no delete path."""
        response = await self._call(
            TIME_OFF_REQUESTS_WITHDRAW,
            path={
                "workspaceId": self._workspace(workspace_id),
                "policyId": policy_id,
                "requestId": request_id,
            },
        )
        return self._adapt(TIME_OFF_REQUESTS_WITHDRAW, response, TimeOffRequestDto)
