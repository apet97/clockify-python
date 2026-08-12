"""Users resource: explicit methods over the user operations."""

import builtins
from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    AddLimitedUsersRequest,
    AddUserToWorkspaceRequest,
    ManagerRoleRequest,
    RoleAssignmentDtoV1,
    UpdateCostRateRequest,
    UpdateUserCustomFieldValueRequest,
    UpdateUserHourlyRateRequest,
    UpdateUserStatusRequest,
    UserDtoV1,
    UserFilterRequest,
    Workspace,
)
from clockify.operations.users import (
    USERS_ADD_LIMITED_TO_WORKSPACE,
    USERS_ADD_TO_WORKSPACE,
    USERS_FILTER,
    USERS_GRANT_MANAGER_ROLE,
    USERS_LIST,
    USERS_LIST_MANAGERS,
    USERS_ME,
    USERS_REVOKE_MANAGER_ROLE,
    USERS_UPDATE_COST_RATE,
    USERS_UPDATE_CUSTOM_FIELD_VALUE,
    USERS_UPDATE_HOURLY_RATE,
    USERS_UPDATE_STATUS,
)
from clockify.resources._base import ResourceBase

_USER_LIST = TypeAdapter(list[UserDtoV1])
_ROLE_ASSIGNMENT_LIST = TypeAdapter(list[RoleAssignmentDtoV1])


ListOfStr = list[str]
ListOfUserDtoV1 = list[UserDtoV1]


class UsersResource(ResourceBase):
    async def add_limited_to_workspace(
        self,
        body: "AddLimitedUsersRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Any:
        """Response is an inline object with no component model; returned as-is."""
        validated = self._coerce(body, AddLimitedUsersRequest)
        response = await self._call(
            USERS_ADD_LIMITED_TO_WORKSPACE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return response.data

    async def add_to_workspace(
        self,
        body: "AddUserToWorkspaceRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
        send_email: str | None = None,
    ) -> Workspace:
        """`send-email` is a required string-enum query parameter ("true"/"false")."""
        validated = self._coerce(body, AddUserToWorkspaceRequest)
        response = await self._call(
            USERS_ADD_TO_WORKSPACE,
            path={"workspaceId": self._workspace(workspace_id)},
            query={"send_email": send_email},
            body=validated,
        )
        return self._adapt(USERS_ADD_TO_WORKSPACE, response, Workspace)

    async def filter(
        self,
        body: "UserFilterRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> builtins.list[UserDtoV1]:
        """Non-mutating filter POST."""
        validated = self._coerce(body, UserFilterRequest)
        response = await self._call(
            USERS_FILTER,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(USERS_FILTER, response, _USER_LIST)

    async def grant_manager_role(
        self,
        user_id: str,
        body: "ManagerRoleRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> builtins.list[RoleAssignmentDtoV1]:
        validated = self._coerce(body, ManagerRoleRequest)
        response = await self._call(
            USERS_GRANT_MANAGER_ROLE,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            body=validated,
        )
        return self._adapt(USERS_GRANT_MANAGER_ROLE, response, _ROLE_ASSIGNMENT_LIST)

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        email: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        account_statuses: "ListOfStr | None" = None,
        name: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        memberships: str | None = None,
        include_roles: bool | None = None,
    ) -> "ListOfUserDtoV1":
        response = await self._call(
            USERS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "email": email,
                "project_id": project_id,
                "status": status,
                "account_statuses": account_statuses,
                "name": name,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
                "memberships": memberships,
                "include_roles": include_roles,
            },
        )
        return self._adapt(USERS_LIST, response, _USER_LIST)

    async def list_managers(
        self,
        user_id: str,
        *,
        workspace_id: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> "ListOfUserDtoV1":
        response = await self._call(
            USERS_LIST_MANAGERS,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            query={
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )
        return self._adapt(USERS_LIST_MANAGERS, response, _USER_LIST)

    async def me(self, *, include_memberships: bool | None = None) -> UserDtoV1:
        response = await self._call(
            USERS_ME, path={}, query={"include_memberships": include_memberships}
        )
        return self._adapt(USERS_ME, response, UserDtoV1)

    async def revoke_manager_role(
        self,
        user_id: str,
        body: "ManagerRoleRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> None:
        """DELETE with a required JSON body; 204 no content."""
        validated = self._coerce(body, ManagerRoleRequest)
        await self._call(
            USERS_REVOKE_MANAGER_ROLE,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            body=validated,
        )
        return None

    async def update_cost_rate(
        self,
        user_id: str,
        body: "UpdateCostRateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Workspace:
        """`amount` is an integer in MINOR units (cents); GET on rate paths 405s."""
        validated = self._coerce(body, UpdateCostRateRequest)
        response = await self._call(
            USERS_UPDATE_COST_RATE,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            body=validated,
        )
        return self._adapt(USERS_UPDATE_COST_RATE, response, Workspace)

    async def update_custom_field_value(
        self,
        user_id: str,
        custom_field_id: str,
        body: "UpdateUserCustomFieldValueRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Any:
        """201 response shape is untyped in the corrected spec; returned as-is."""
        validated = self._coerce(body, UpdateUserCustomFieldValueRequest)
        response = await self._call(
            USERS_UPDATE_CUSTOM_FIELD_VALUE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "userId": user_id,
                "customFieldId": custom_field_id,
            },
            body=validated,
        )
        return response.data

    async def update_hourly_rate(
        self,
        user_id: str,
        body: "UpdateUserHourlyRateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Workspace:
        """`amount` is an integer in MINOR units (cents); GET on rate paths 405s."""
        validated = self._coerce(body, UpdateUserHourlyRateRequest)
        response = await self._call(
            USERS_UPDATE_HOURLY_RATE,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            body=validated,
        )
        return self._adapt(USERS_UPDATE_HOURLY_RATE, response, Workspace)

    async def update_status(
        self,
        user_id: str,
        body: "UpdateUserStatusRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> Workspace:
        validated = self._coerce(body, UpdateUserStatusRequest)
        response = await self._call(
            USERS_UPDATE_STATUS,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            body=validated,
        )
        return self._adapt(USERS_UPDATE_STATUS, response, Workspace)
