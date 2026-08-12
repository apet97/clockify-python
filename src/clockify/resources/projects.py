"""Projects resource: explicit methods over the project operations."""

import builtins
from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    AssignRemoveUsersRequest,
    CreateProjectFromTemplateRequest,
    CreateProjectRequest,
    Project,
    RateRequest,
    UpdateProjectEstimateRequest,
    UpdateProjectMembershipsRequest,
    UpdateProjectRequest,
    UpdateProjectTemplateRequest,
)
from clockify.operations.projects import (
    PROJECTS_CREATE,
    PROJECTS_CREATE_FROM_TEMPLATE,
    PROJECTS_DELETE,
    PROJECTS_GET,
    PROJECTS_LIST,
    PROJECTS_SET_MEMBERS,
    PROJECTS_UPDATE,
    PROJECTS_UPDATE_ESTIMATE,
    PROJECTS_UPDATE_MEMBERSHIPS,
    PROJECTS_UPDATE_TEMPLATE,
    PROJECTS_UPDATE_USER_COST_RATE,
    PROJECTS_UPDATE_USER_HOURLY_RATE,
)
from clockify.resources._base import ResourceBase

_PROJECT_LIST = TypeAdapter(list[Project])


class ProjectsResource(ResourceBase):
    async def create(
        self,
        body: "CreateProjectRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Project:
        """A deleted project's name stays reserved — 'already exists' errors need a distinct name."""
        validated = self._coerce(body, CreateProjectRequest)
        response = await self._call(
            PROJECTS_CREATE, path={"workspaceId": self._workspace(workspace_id)}, body=validated
        )
        return self._adapt(PROJECTS_CREATE, response, Project)

    async def create_from_template(
        self,
        body: "CreateProjectFromTemplateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Project:
        validated = self._coerce(body, CreateProjectFromTemplateRequest)
        response = await self._call(
            PROJECTS_CREATE_FROM_TEMPLATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(PROJECTS_CREATE_FROM_TEMPLATE, response, Project)

    async def delete(self, project_id: str, *, workspace_id: str | None = None) -> Project:
        """DELETE of an ACTIVE project is rejected — archive first via update (archived: true)."""
        response = await self._call(
            PROJECTS_DELETE,
            path={"workspaceId": self._workspace(workspace_id), "projectId": project_id},
        )
        return self._adapt(PROJECTS_DELETE, response, Project)

    async def get(
        self,
        project_id: str,
        *,
        workspace_id: str | None = None,
        hydrated: bool | None = None,
        custom_field_entity_type: str | None = None,
        expense_limit: int | None = None,
        expense_date: str | None = None,
    ) -> Project:
        """Deleted, never-existing, and foreign-workspace ids all return 400 code 501, never 404."""
        response = await self._call(
            PROJECTS_GET,
            path={"workspaceId": self._workspace(workspace_id), "projectId": project_id},
            query={
                "hydrated": hydrated,
                "custom_field_entity_type": custom_field_entity_type,
                "expense_limit": expense_limit,
                "expense_date": expense_date,
            },
        )
        return self._adapt(PROJECTS_GET, response, Project)

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        name: str | None = None,
        strict_name_search: str | None = None,
        archived: bool | None = None,
        billable: bool | None = None,
        clients: builtins.list[str] | None = None,
        contains_client: bool | None = None,
        client_status: str | None = None,
        users: builtins.list[str] | None = None,
        contains_user: bool | None = None,
        user_status: str | None = None,
        is_template: bool | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        hydrated: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        access: str | None = None,
        expense_limit: int | None = None,
        expense_date: str | None = None,
        user_groups: builtins.list[str] | None = None,
        contains_group: bool | None = None,
    ) -> builtins.list[Project]:
        """Omitting `archived` returns archived AND active rows; only archived=false restricts."""
        response = await self._call(
            PROJECTS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "name": name,
                "strict_name_search": strict_name_search,
                "archived": archived,
                "billable": billable,
                "clients": clients,
                "contains_client": contains_client,
                "client_status": client_status,
                "users": users,
                "contains_user": contains_user,
                "user_status": user_status,
                "is_template": is_template,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "hydrated": hydrated,
                "page": page,
                "page_size": page_size,
                "access": access,
                "expense_limit": expense_limit,
                "expense_date": expense_date,
                "user_groups": user_groups,
                "contains_group": contains_group,
            },
        )
        return self._adapt(PROJECTS_LIST, response, _PROJECT_LIST)

    async def set_members(
        self,
        project_id: str,
        body: "AssignRemoveUsersRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Project:
        """Multi-entity assign/remove in one call."""
        validated = self._coerce(body, AssignRemoveUsersRequest)
        response = await self._call(
            PROJECTS_SET_MEMBERS,
            path={"workspaceId": self._workspace(workspace_id), "projectId": project_id},
            body=validated,
        )
        return self._adapt(PROJECTS_SET_MEMBERS, response, Project)

    async def update(
        self,
        project_id: str,
        body: "UpdateProjectRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Project:
        """Replace-PUT with mixed omission semantics: resend `billable` and GET-side `public` as `isPublic` every time (omission can reset them); rates are preserved under omission."""
        validated = self._coerce(body, UpdateProjectRequest)
        response = await self._call(
            PROJECTS_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "projectId": project_id},
            body=validated,
        )
        return self._adapt(PROJECTS_UPDATE, response, Project)

    async def update_estimate(
        self,
        project_id: str,
        body: "UpdateProjectEstimateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Project:
        """Dedicated PATCH for estimates — prefer over carrying estimates through the replace-PUT."""
        validated = self._coerce(body, UpdateProjectEstimateRequest)
        response = await self._call(
            PROJECTS_UPDATE_ESTIMATE,
            path={"workspaceId": self._workspace(workspace_id), "projectId": project_id},
            body=validated,
        )
        return self._adapt(PROJECTS_UPDATE_ESTIMATE, response, Project)

    async def update_memberships(
        self,
        project_id: str,
        body: "UpdateProjectMembershipsRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Project:
        validated = self._coerce(body, UpdateProjectMembershipsRequest)
        response = await self._call(
            PROJECTS_UPDATE_MEMBERSHIPS,
            path={"workspaceId": self._workspace(workspace_id), "projectId": project_id},
            body=validated,
        )
        return self._adapt(PROJECTS_UPDATE_MEMBERSHIPS, response, Project)

    async def update_template(
        self,
        project_id: str,
        body: "UpdateProjectTemplateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Project:
        validated = self._coerce(body, UpdateProjectTemplateRequest)
        response = await self._call(
            PROJECTS_UPDATE_TEMPLATE,
            path={"workspaceId": self._workspace(workspace_id), "projectId": project_id},
            body=validated,
        )
        return self._adapt(PROJECTS_UPDATE_TEMPLATE, response, Project)

    async def update_user_cost_rate(
        self,
        project_id: str,
        user_id: str,
        body: "RateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Project:
        """Rate `amount` is an integer in minor units (cents); GET on rate paths 405s — read current value from the project document."""
        validated = self._coerce(body, RateRequest)
        response = await self._call(
            PROJECTS_UPDATE_USER_COST_RATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
                "userId": user_id,
            },
            body=validated,
        )
        return self._adapt(PROJECTS_UPDATE_USER_COST_RATE, response, Project)

    async def update_user_hourly_rate(
        self,
        project_id: str,
        user_id: str,
        body: "RateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Project:
        """Rate `amount` is an integer in minor units (cents); GET on rate paths 405s — read current value from the project document."""
        validated = self._coerce(body, RateRequest)
        response = await self._call(
            PROJECTS_UPDATE_USER_HOURLY_RATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
                "userId": user_id,
            },
            body=validated,
        )
        return self._adapt(PROJECTS_UPDATE_USER_HOURLY_RATE, response, Project)
