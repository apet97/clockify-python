"""Scheduling resource: explicit methods over the scheduling operations."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    AssignmentListItem,
    ChangeRecurringPeriodRequest,
    CopyAssignmentRequest,
    CreateRecurringAssignmentRequest,
    ProjectAssignmentsTotal,
    ProjectTotalsRequest,
    PublishAssignmentsRequest,
    SchedulingAssignment,
    UpdateRecurringAssignmentRequest,
    UserCapacityTotal,
    UserCapacityTotalsRequest,
)
from clockify.operations.scheduling import (
    SCHEDULING_CHANGE_RECURRING_PERIOD,
    SCHEDULING_COPY_ASSIGNMENT,
    SCHEDULING_CREATE_RECURRING,
    SCHEDULING_DELETE_RECURRING,
    SCHEDULING_GET_FILTERED_USER_CAPACITY,
    SCHEDULING_GET_PROJECT_TOTALS,
    SCHEDULING_GET_USER_CAPACITY,
    SCHEDULING_LIST_ASSIGNMENTS,
    SCHEDULING_LIST_PROJECT_TOTALS,
    SCHEDULING_PUBLISH_ASSIGNMENTS,
    SCHEDULING_UPDATE_RECURRING,
)
from clockify.resources._base import ResourceBase

_ASSIGNMENT_LIST = TypeAdapter(list[SchedulingAssignment])
_ASSIGNMENT_ITEM_LIST = TypeAdapter(list[AssignmentListItem])
_USER_CAPACITY_LIST = TypeAdapter(list[UserCapacityTotal])
_PROJECT_TOTALS_LIST = TypeAdapter(list[ProjectAssignmentsTotal])


class SchedulingResource(ResourceBase):
    async def change_recurring_period(
        self,
        assignment_id: str,
        body: "ChangeRecurringPeriodRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> list[SchedulingAssignment]:
        """PUT with unproven omission behavior — treat as replacement and resend all fields."""
        validated = self._coerce(body, ChangeRecurringPeriodRequest)
        response = await self._call(
            SCHEDULING_CHANGE_RECURRING_PERIOD,
            path={
                "workspaceId": self._workspace(workspace_id),
                "assignmentId": assignment_id,
            },
            body=validated,
        )
        return self._adapt(SCHEDULING_CHANGE_RECURRING_PERIOD, response, _ASSIGNMENT_LIST)

    async def copy_assignment(
        self,
        assignment_id: str,
        body: "CopyAssignmentRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> list[SchedulingAssignment]:
        validated = self._coerce(body, CopyAssignmentRequest)
        response = await self._call(
            SCHEDULING_COPY_ASSIGNMENT,
            path={
                "workspaceId": self._workspace(workspace_id),
                "assignmentId": assignment_id,
            },
            body=validated,
        )
        return self._adapt(SCHEDULING_COPY_ASSIGNMENT, response, _ASSIGNMENT_LIST)

    async def create_recurring(
        self,
        body: "CreateRecurringAssignmentRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> list[SchedulingAssignment]:
        """Returns a bare array (one per occurrence); the created-entity id is element [0]."""
        validated = self._coerce(body, CreateRecurringAssignmentRequest)
        response = await self._call(
            SCHEDULING_CREATE_RECURRING,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(SCHEDULING_CREATE_RECURRING, response, _ASSIGNMENT_LIST)

    async def delete_recurring(
        self,
        assignment_id: str,
        *,
        workspace_id: str | None = None,
        series_update_option: str | None = None,
    ) -> list[SchedulingAssignment]:
        response = await self._call(
            SCHEDULING_DELETE_RECURRING,
            path={
                "workspaceId": self._workspace(workspace_id),
                "assignmentId": assignment_id,
            },
            query={"series_update_option": series_update_option},
        )
        return self._adapt(SCHEDULING_DELETE_RECURRING, response, _ASSIGNMENT_LIST)

    async def get_filtered_user_capacity(
        self,
        body: "UserCapacityTotalsRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> list[UserCapacityTotal]:
        validated = self._coerce(body, UserCapacityTotalsRequest)
        response = await self._call(
            SCHEDULING_GET_FILTERED_USER_CAPACITY,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(SCHEDULING_GET_FILTERED_USER_CAPACITY, response, _USER_CAPACITY_LIST)

    async def get_project_totals(
        self,
        project_id: str,
        *,
        workspace_id: str | None = None,
        start: str,
        end: str,
    ) -> ProjectAssignmentsTotal:
        """Live Clockify requires start and end; the GET returns 400 without them."""
        response = await self._call(
            SCHEDULING_GET_PROJECT_TOTALS,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
            },
            query={"start": start, "end": end},
        )
        return self._adapt(SCHEDULING_GET_PROJECT_TOTALS, response, ProjectAssignmentsTotal)

    async def get_user_capacity(
        self,
        user_id: str,
        *,
        workspace_id: str | None = None,
        start: str,
        end: str,
        page: int | None = None,
        page_size: int | None = None,
    ) -> UserCapacityTotal:
        """start and end are required (yyyy-MM-ddThh:mm:ssZ)."""
        response = await self._call(
            SCHEDULING_GET_USER_CAPACITY,
            path={
                "workspaceId": self._workspace(workspace_id),
                "userId": user_id,
            },
            query={"page": page, "page_size": page_size, "start": start, "end": end},
        )
        return self._adapt(SCHEDULING_GET_USER_CAPACITY, response, UserCapacityTotal)

    async def list_assignments(
        self,
        *,
        workspace_id: str | None = None,
        start: str,
        end: str,
        name: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[AssignmentListItem]:
        """start and end are required by live Clockify."""
        response = await self._call(
            SCHEDULING_LIST_ASSIGNMENTS,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "name": name,
                "start": start,
                "end": end,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )
        return self._adapt(SCHEDULING_LIST_ASSIGNMENTS, response, _ASSIGNMENT_ITEM_LIST)

    async def list_project_totals(
        self,
        body: "ProjectTotalsRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> list[ProjectAssignmentsTotal]:
        """Body requires start+end; it has no projectId (silently dropped) —
        use get_project_totals for one project."""
        validated = self._coerce(body, ProjectTotalsRequest)
        response = await self._call(
            SCHEDULING_LIST_PROJECT_TOTALS,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(SCHEDULING_LIST_PROJECT_TOTALS, response, _PROJECT_TOTALS_LIST)

    async def publish_assignments(
        self,
        body: "PublishAssignmentsRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> None:
        """Range-scoped bulk publish across the whole workspace schedule."""
        validated = self._coerce(body, PublishAssignmentsRequest)
        await self._call(
            SCHEDULING_PUBLISH_ASSIGNMENTS,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return None

    async def update_recurring(
        self,
        assignment_id: str,
        body: "UpdateRecurringAssignmentRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> list[SchedulingAssignment]:
        validated = self._coerce(body, UpdateRecurringAssignmentRequest)
        response = await self._call(
            SCHEDULING_UPDATE_RECURRING,
            path={
                "workspaceId": self._workspace(workspace_id),
                "assignmentId": assignment_id,
            },
            body=validated,
        )
        return self._adapt(SCHEDULING_UPDATE_RECURRING, response, _ASSIGNMENT_LIST)
