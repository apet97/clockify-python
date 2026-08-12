"""User groups resource: explicit methods over the user-group operations."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import AddUserToGroupRequest, UserGroupDtoV1, UserGroupRequest
from clockify.operations.user_groups import (
    USER_GROUPS_ADD_MEMBERS,
    USER_GROUPS_CREATE,
    USER_GROUPS_DELETE,
    USER_GROUPS_LIST,
    USER_GROUPS_REMOVE_MEMBER,
    USER_GROUPS_UPDATE,
)
from clockify.resources._base import ResourceBase

_GROUP_LIST = TypeAdapter(list[UserGroupDtoV1])


class UserGroupsResource(ResourceBase):
    async def add_members(
        self,
        group_id: str,
        body: "AddUserToGroupRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> UserGroupDtoV1:
        validated = self._coerce(body, AddUserToGroupRequest)
        response = await self._call(
            USER_GROUPS_ADD_MEMBERS,
            path={"workspaceId": self._workspace(workspace_id), "groupId": group_id},
            body=validated,
        )
        return self._adapt(USER_GROUPS_ADD_MEMBERS, response, UserGroupDtoV1)

    async def create(
        self,
        body: "UserGroupRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> UserGroupDtoV1:
        validated = self._coerce(body, UserGroupRequest)
        response = await self._call(
            USER_GROUPS_CREATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(USER_GROUPS_CREATE, response, UserGroupDtoV1)

    async def delete(self, group_id: str, *, workspace_id: str | None = None) -> UserGroupDtoV1:
        """Delete a group. Clockify answers 200 with the deleted group document."""
        response = await self._call(
            USER_GROUPS_DELETE,
            path={"workspaceId": self._workspace(workspace_id), "groupId": group_id},
        )
        return self._adapt(USER_GROUPS_DELETE, response, UserGroupDtoV1)

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        project_id: str | None = None,
        name: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        include_team_managers: bool | None = None,
    ) -> list[UserGroupDtoV1]:
        response = await self._call(
            USER_GROUPS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "project_id": project_id,
                "name": name,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
                "include_team_managers": include_team_managers,
            },
        )
        return self._adapt(USER_GROUPS_LIST, response, _GROUP_LIST)

    async def remove_member(
        self, group_id: str, user_id: str, *, workspace_id: str | None = None
    ) -> UserGroupDtoV1:
        response = await self._call(
            USER_GROUPS_REMOVE_MEMBER,
            path={
                "workspaceId": self._workspace(workspace_id),
                "groupId": group_id,
                "userId": user_id,
            },
        )
        return self._adapt(USER_GROUPS_REMOVE_MEMBER, response, UserGroupDtoV1)

    async def update(
        self,
        group_id: str,
        body: "UserGroupRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> UserGroupDtoV1:
        """PUT omission behavior is unproven; treat as a potential full replacement."""
        validated = self._coerce(body, UserGroupRequest)
        response = await self._call(
            USER_GROUPS_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "groupId": group_id},
            body=validated,
        )
        return self._adapt(USER_GROUPS_UPDATE, response, UserGroupDtoV1)
