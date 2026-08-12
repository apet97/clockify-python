"""Member profiles resource: explicit methods over the member-profile operations."""

from collections.abc import Mapping
from typing import Any

from clockify.models import MemberProfileDtoV1, MemberProfileUpdateRequest
from clockify.operations.member_profiles import (
    MEMBER_PROFILES_GET,
    MEMBER_PROFILES_UPDATE,
)
from clockify.resources._base import ResourceBase


class MemberProfilesResource(ResourceBase):
    async def get(self, user_id: str, *, workspace_id: str | None = None) -> MemberProfileDtoV1:
        response = await self._call(
            MEMBER_PROFILES_GET,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
        )
        return self._adapt(MEMBER_PROFILES_GET, response, MemberProfileDtoV1)

    async def update(
        self,
        user_id: str,
        body: "MemberProfileUpdateRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> MemberProfileDtoV1:
        validated = self._coerce(body, MemberProfileUpdateRequest)
        response = await self._call(
            MEMBER_PROFILES_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            body=validated,
        )
        return self._adapt(MEMBER_PROFILES_UPDATE, response, MemberProfileDtoV1)
