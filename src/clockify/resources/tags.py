"""Tags resource: explicit methods over the tag operations."""

import builtins
from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import TagCreate, TagDto
from clockify.operations.tags import (
    TAGS_CREATE,
    TAGS_DELETE,
    TAGS_GET,
    TAGS_LIST,
    TAGS_UPDATE,
)
from clockify.resources._base import ResourceBase

_TAG_LIST = TypeAdapter(list[TagDto])


class TagsResource(ResourceBase):
    async def create(
        self, body: "TagCreate | Mapping[str, Any]", *, workspace_id: str | None = None
    ) -> TagDto:
        validated = self._coerce(body, TagCreate)
        response = await self._call(
            TAGS_CREATE, path={"workspaceId": self._workspace(workspace_id)}, body=validated
        )
        return self._adapt(TAGS_CREATE, response, TagDto)

    async def delete(self, tag_id: str, *, workspace_id: str | None = None) -> TagDto:
        """Delete a tag. Clockify answers 200 with the deleted tag entity."""
        response = await self._call(
            TAGS_DELETE, path={"workspaceId": self._workspace(workspace_id), "tagId": tag_id}
        )
        return self._adapt(TAGS_DELETE, response, TagDto)

    async def get(self, tag_id: str, *, workspace_id: str | None = None) -> TagDto:
        response = await self._call(
            TAGS_GET, path={"workspaceId": self._workspace(workspace_id), "tagId": tag_id}
        )
        return self._adapt(TAGS_GET, response, TagDto)

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        name: str | None = None,
        strict_name_search: str | None = None,
        excluded_ids: builtins.list[str] | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        archived: bool | None = None,
    ) -> builtins.list[TagDto]:
        response = await self._call(
            TAGS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "name": name,
                "strict_name_search": strict_name_search,
                "excluded_ids": excluded_ids,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
                "archived": archived,
            },
        )
        return self._adapt(TAGS_LIST, response, _TAG_LIST)

    async def update(
        self,
        tag_id: str,
        body: Mapping[str, Any],
        *,
        workspace_id: str | None = None,
    ) -> TagDto:
        """Full replacement: an omitted `archived` resets to false — resend it."""
        response = await self._call(
            TAGS_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "tagId": tag_id},
            body=dict(body),
        )
        return self._adapt(TAGS_UPDATE, response, TagDto)
