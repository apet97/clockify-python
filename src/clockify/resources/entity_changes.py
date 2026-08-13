"""Entity changes resource: experimental created/deleted/updated change feeds."""

from pydantic import TypeAdapter

from clockify.models import EntityChangeDocument
from clockify.operations.entity_changes import (
    ENTITY_CHANGES_LIST_CREATED,
    ENTITY_CHANGES_LIST_DELETED,
    ENTITY_CHANGES_LIST_UPDATED,
)
from clockify.resources._base import ResourceBase

_DOCUMENT_LIST = TypeAdapter(list[EntityChangeDocument])


class EntityChangesResource(ResourceBase):
    async def list_created(
        self,
        *,
        workspace_id: str | None = None,
        type: list[str],
        start: str | None = None,
        end: str | None = None,
        page: str | None = None,
        limit: str | None = None,
    ) -> list[EntityChangeDocument]:
        """`type` is required by the live API; page/limit are string-typed on the wire."""
        response = await self._call(
            ENTITY_CHANGES_LIST_CREATED,
            path={"workspaceId": self._workspace(workspace_id)},
            query={"type": type, "start": start, "end": end, "page": page, "limit": limit},
        )
        return self._adapt(ENTITY_CHANGES_LIST_CREATED, response, _DOCUMENT_LIST)

    async def list_deleted(
        self,
        *,
        workspace_id: str | None = None,
        type: list[str],
        start: str | None = None,
        end: str | None = None,
        page: str | None = None,
        limit: str | None = None,
    ) -> list[EntityChangeDocument]:
        """`type` is required by the live API; page/limit are string-typed on the wire."""
        response = await self._call(
            ENTITY_CHANGES_LIST_DELETED,
            path={"workspaceId": self._workspace(workspace_id)},
            query={"type": type, "start": start, "end": end, "page": page, "limit": limit},
        )
        return self._adapt(ENTITY_CHANGES_LIST_DELETED, response, _DOCUMENT_LIST)

    async def list_updated(
        self,
        *,
        workspace_id: str | None = None,
        type: list[str],
        start: str | None = None,
        end: str | None = None,
        page: str | None = None,
        limit: str | None = None,
    ) -> list[EntityChangeDocument]:
        """`type` is required by the live API; page/limit are string-typed on the wire."""
        response = await self._call(
            ENTITY_CHANGES_LIST_UPDATED,
            path={"workspaceId": self._workspace(workspace_id)},
            query={"type": type, "start": start, "end": end, "page": page, "limit": limit},
        )
        return self._adapt(ENTITY_CHANGES_LIST_UPDATED, response, _DOCUMENT_LIST)
