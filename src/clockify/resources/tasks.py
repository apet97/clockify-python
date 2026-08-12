"""Tasks resource: explicit methods over the task operations."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import RateUpdateRequest, Task, TaskCreateRequest, TaskUpdateRequest
from clockify.operations.tasks import (
    TASKS_CREATE,
    TASKS_DELETE,
    TASKS_GET,
    TASKS_LIST,
    TASKS_UPDATE,
    TASKS_UPDATE_BILLABLE_RATE,
    TASKS_UPDATE_COST_RATE,
)
from clockify.resources._base import ResourceBase

_TASK_LIST = TypeAdapter(list[Task])


class TasksResource(ResourceBase):
    async def create(
        self,
        project_id: str,
        body: "TaskCreateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
        contains_assignee: bool | None = None,
    ) -> Task:
        validated = self._coerce(body, TaskCreateRequest)
        response = await self._call(
            TASKS_CREATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
            },
            query={"contains_assignee": contains_assignee},
            body=validated,
        )
        return self._adapt(TASKS_CREATE, response, Task)

    async def delete(
        self, project_id: str, task_id: str, *, workspace_id: str | None = None
    ) -> Task:
        """Clockify rejects DELETE of an ACTIVE task: mark it status DONE first
        (GET, then PUT overlay `status: "DONE"`, then DELETE)."""
        response = await self._call(
            TASKS_DELETE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
        )
        return self._adapt(TASKS_DELETE, response, Task)

    async def get(self, project_id: str, task_id: str, *, workspace_id: str | None = None) -> Task:
        response = await self._call(
            TASKS_GET,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
        )
        return self._adapt(TASKS_GET, response, Task)

    async def list(
        self,
        project_id: str,
        *,
        workspace_id: str | None = None,
        name: str | None = None,
        strict_name_search: str | None = None,
        is_active: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
    ) -> list[Task]:
        response = await self._call(
            TASKS_LIST,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
            },
            query={
                "name": name,
                "strict_name_search": strict_name_search,
                "is_active": is_active,
                "page": page,
                "page_size": page_size,
                "sort_column": sort_column,
                "sort_order": sort_order,
            },
        )
        return self._adapt(TASKS_LIST, response, _TASK_LIST)

    async def update(
        self,
        project_id: str,
        task_id: str,
        body: "TaskUpdateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
        contains_assignee: bool | None = None,
        membership_status: str | None = None,
    ) -> Task:
        """Proven full replacement: resend all fields or omitted ones are lost."""
        validated = self._coerce(body, TaskUpdateRequest)
        response = await self._call(
            TASKS_UPDATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
            query={
                "contains_assignee": contains_assignee,
                "membership_status": membership_status,
            },
            body=validated,
        )
        return self._adapt(TASKS_UPDATE, response, Task)

    async def update_billable_rate(
        self,
        project_id: str,
        task_id: str,
        body: "RateUpdateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Task:
        """Rate `amount` is an integer in minor units (cents); no scaling applied."""
        validated = self._coerce(body, RateUpdateRequest)
        response = await self._call(
            TASKS_UPDATE_BILLABLE_RATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
            body=validated,
        )
        return self._adapt(TASKS_UPDATE_BILLABLE_RATE, response, Task)

    async def update_cost_rate(
        self,
        project_id: str,
        task_id: str,
        body: "RateUpdateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Task:
        """Rate `amount` is an integer in minor units (cents); no scaling applied."""
        validated = self._coerce(body, RateUpdateRequest)
        response = await self._call(
            TASKS_UPDATE_COST_RATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
            body=validated,
        )
        return self._adapt(TASKS_UPDATE_COST_RATE, response, Task)
