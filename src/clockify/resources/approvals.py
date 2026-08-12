"""Approvals resource: explicit methods over the approval-request operations."""

import builtins
from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    ApprovalRequestDtoV1,
    ApprovalRequestListItem,
    CreateApprovalRequestNoType,
    SubmitApprovalRequestRequest,
    UpdateApprovalRequestRequest,
)
from clockify.operations.approvals import (
    APPROVALS_LIST,
    APPROVALS_RESUBMIT,
    APPROVALS_RESUBMIT_FOR_USER,
    APPROVALS_SUBMIT,
    APPROVALS_SUBMIT_FOR_USER,
    APPROVALS_SUBMIT_FOR_USER_WITH_TYPE,
    APPROVALS_SUBMIT_WITH_TYPE,
    APPROVALS_UPDATE_STATUS,
)
from clockify.resources._base import ResourceBase

_APPROVAL_LIST = TypeAdapter(list[ApprovalRequestListItem])


class ApprovalsResource(ResourceBase):
    async def list(
        self,
        *,
        workspace_id: str | None = None,
        status: str | None = None,
        sort_column: str | None = None,
        types: builtins.list[str] | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> builtins.list[ApprovalRequestListItem]:
        response = await self._call(
            APPROVALS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "status": status,
                "sort_column": sort_column,
                "types": types,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )
        return self._adapt(APPROVALS_LIST, response, _APPROVAL_LIST)

    async def resubmit(
        self,
        body: "SubmitApprovalRequestRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ApprovalRequestDtoV1:
        validated = self._coerce(body, SubmitApprovalRequestRequest)
        response = await self._call(
            APPROVALS_RESUBMIT,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(APPROVALS_RESUBMIT, response, ApprovalRequestDtoV1)

    async def resubmit_for_user(
        self,
        user_id: str,
        body: "SubmitApprovalRequestRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ApprovalRequestDtoV1:
        validated = self._coerce(body, SubmitApprovalRequestRequest)
        response = await self._call(
            APPROVALS_RESUBMIT_FOR_USER,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            body=validated,
        )
        return self._adapt(APPROVALS_RESUBMIT_FOR_USER, response, ApprovalRequestDtoV1)

    async def submit(
        self,
        body: "SubmitApprovalRequestRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ApprovalRequestDtoV1:
        validated = self._coerce(body, SubmitApprovalRequestRequest)
        response = await self._call(
            APPROVALS_SUBMIT,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(APPROVALS_SUBMIT, response, ApprovalRequestDtoV1)

    async def submit_for_user(
        self,
        user_id: str,
        body: "SubmitApprovalRequestRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ApprovalRequestDtoV1:
        validated = self._coerce(body, SubmitApprovalRequestRequest)
        response = await self._call(
            APPROVALS_SUBMIT_FOR_USER,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            body=validated,
        )
        return self._adapt(APPROVALS_SUBMIT_FOR_USER, response, ApprovalRequestDtoV1)

    async def submit_for_user_with_type(
        self,
        user_id: str,
        type: str,
        body: "CreateApprovalRequestNoType | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ApprovalRequestDtoV1:
        """`type` is TIMESHEET | EXPENSE | TIMESHEET_AND_EXPENSE."""
        validated = self._coerce(body, CreateApprovalRequestNoType)
        response = await self._call(
            APPROVALS_SUBMIT_FOR_USER_WITH_TYPE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "userId": user_id,
                "type": type,
            },
            body=validated,
        )
        return self._adapt(APPROVALS_SUBMIT_FOR_USER_WITH_TYPE, response, ApprovalRequestDtoV1)

    async def submit_with_type(
        self,
        approval_request_id: str,
        body: "CreateApprovalRequestNoType | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ApprovalRequestDtoV1:
        """`approval_request_id` is actually the approval type (TIMESHEET | EXPENSE)."""
        validated = self._coerce(body, CreateApprovalRequestNoType)
        response = await self._call(
            APPROVALS_SUBMIT_WITH_TYPE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "approvalRequestId": approval_request_id,
            },
            body=validated,
        )
        return self._adapt(APPROVALS_SUBMIT_WITH_TYPE, response, ApprovalRequestDtoV1)

    async def update_status(
        self,
        approval_request_id: str,
        body: "UpdateApprovalRequestRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> ApprovalRequestDtoV1:
        validated = self._coerce(body, UpdateApprovalRequestRequest)
        response = await self._call(
            APPROVALS_UPDATE_STATUS,
            path={
                "workspaceId": self._workspace(workspace_id),
                "approvalRequestId": approval_request_id,
            },
            body=validated,
        )
        return self._adapt(APPROVALS_UPDATE_STATUS, response, ApprovalRequestDtoV1)
