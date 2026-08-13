"""Custom fields resource: workspace- and project-level custom field operations."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    CreateCustomFieldRequest,
    CustomField,
    UpdateCustomFieldRequest,
    UpdateProjectCustomFieldRequest,
)
from clockify.operations.custom_fields import (
    CUSTOM_FIELDS_CREATE_FOR_WORKSPACE,
    CUSTOM_FIELDS_DELETE_FOR_WORKSPACE,
    CUSTOM_FIELDS_LIST_FOR_PROJECT,
    CUSTOM_FIELDS_LIST_FOR_WORKSPACE,
    CUSTOM_FIELDS_REMOVE_FROM_PROJECT,
    CUSTOM_FIELDS_UPDATE_FOR_PROJECT,
    CUSTOM_FIELDS_UPDATE_FOR_WORKSPACE,
)
from clockify.resources._base import ResourceBase

_CUSTOM_FIELD_LIST = TypeAdapter(list[CustomField])


class CustomFieldsResource(ResourceBase):
    async def create_for_workspace(
        self,
        body: "CreateCustomFieldRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> CustomField:
        validated = self._coerce(body, CreateCustomFieldRequest)
        response = await self._call(
            CUSTOM_FIELDS_CREATE_FOR_WORKSPACE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(CUSTOM_FIELDS_CREATE_FOR_WORKSPACE, response, CustomField)

    async def delete_for_workspace(
        self, custom_field_id: str, *, workspace_id: str | None = None
    ) -> None:
        await self._call(
            CUSTOM_FIELDS_DELETE_FOR_WORKSPACE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "customFieldId": custom_field_id,
            },
        )
        return None

    async def list_for_project(
        self,
        project_id: str,
        *,
        workspace_id: str | None = None,
        status: str | None = None,
        entity_type: list[str] | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[CustomField]:
        response = await self._call(
            CUSTOM_FIELDS_LIST_FOR_PROJECT,
            path={"workspaceId": self._workspace(workspace_id), "projectId": project_id},
            query={
                "status": status,
                "entity_type": entity_type,
                "page": page,
                "page_size": page_size,
            },
        )
        return self._adapt(CUSTOM_FIELDS_LIST_FOR_PROJECT, response, _CUSTOM_FIELD_LIST)

    async def list_for_workspace(
        self,
        *,
        workspace_id: str | None = None,
        name: str | None = None,
        status: str | None = None,
        entity_type: list[str] | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[CustomField]:
        response = await self._call(
            CUSTOM_FIELDS_LIST_FOR_WORKSPACE,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "name": name,
                "status": status,
                "entity_type": entity_type,
                "page": page,
                "page_size": page_size,
            },
        )
        return self._adapt(CUSTOM_FIELDS_LIST_FOR_WORKSPACE, response, _CUSTOM_FIELD_LIST)

    async def remove_from_project(
        self,
        project_id: str,
        custom_field_id: str,
        *,
        workspace_id: str | None = None,
    ) -> CustomField:
        response = await self._call(
            CUSTOM_FIELDS_REMOVE_FROM_PROJECT,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
                "customFieldId": custom_field_id,
            },
        )
        return self._adapt(CUSTOM_FIELDS_REMOVE_FROM_PROJECT, response, CustomField)

    async def update_for_project(
        self,
        project_id: str,
        custom_field_id: str,
        body: "UpdateProjectCustomFieldRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> CustomField:
        validated = self._coerce(body, UpdateProjectCustomFieldRequest)
        response = await self._call(
            CUSTOM_FIELDS_UPDATE_FOR_PROJECT,
            path={
                "workspaceId": self._workspace(workspace_id),
                "projectId": project_id,
                "customFieldId": custom_field_id,
            },
            body=validated,
        )
        return self._adapt(CUSTOM_FIELDS_UPDATE_FOR_PROJECT, response, CustomField)

    async def update_for_workspace(
        self,
        custom_field_id: str,
        body: "UpdateCustomFieldRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> CustomField:
        """PUT omission behavior unproven; treat as full replacement and resend every field."""
        validated = self._coerce(body, UpdateCustomFieldRequest)
        response = await self._call(
            CUSTOM_FIELDS_UPDATE_FOR_WORKSPACE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "customFieldId": custom_field_id,
            },
            body=validated,
        )
        return self._adapt(CUSTOM_FIELDS_UPDATE_FOR_WORKSPACE, response, CustomField)
