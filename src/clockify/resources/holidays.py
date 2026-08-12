"""Holidays resource: explicit methods over the holiday operations."""

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import (
    CreateHolidayRequest,
    HolidayDetailsDto,
    HolidayDto,
    UpdateHolidayRequest,
)
from clockify.operations.holidays import (
    HOLIDAYS_CREATE,
    HOLIDAYS_DELETE,
    HOLIDAYS_LIST,
    HOLIDAYS_LIST_IN_PERIOD,
    HOLIDAYS_UPDATE,
)
from clockify.resources._base import ResourceBase

_HOLIDAY_LIST = TypeAdapter(list[HolidayDto])


ListOfHolidayDto = list[HolidayDto]


class HolidaysResource(ResourceBase):
    async def create(
        self,
        body: "CreateHolidayRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> HolidayDto:
        """Assignment must be a {contains, ids, status} filter under users/userGroups."""
        validated = self._coerce(body, CreateHolidayRequest)
        response = await self._call(
            HOLIDAYS_CREATE, path={"workspaceId": self._workspace(workspace_id)}, body=validated
        )
        return self._adapt(HOLIDAYS_CREATE, response, HolidayDto)

    async def delete(
        self, holiday_id: str, *, workspace_id: str | None = None
    ) -> HolidayDetailsDto:
        """Delete a holiday. Clockify answers 200 with the deleted HolidayDetailsDto."""
        response = await self._call(
            HOLIDAYS_DELETE,
            path={"workspaceId": self._workspace(workspace_id), "holidayId": holiday_id},
        )
        return self._adapt(HOLIDAYS_DELETE, response, HolidayDetailsDto)

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        assigned_to: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> "ListOfHolidayDto":
        response = await self._call(
            HOLIDAYS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={"assigned_to": assigned_to, "page": page, "page_size": page_size},
        )
        return self._adapt(HOLIDAYS_LIST, response, _HOLIDAY_LIST)

    async def list_in_period(
        self,
        *,
        workspace_id: str | None = None,
        assigned_to: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> "ListOfHolidayDto":
        """Live Clockify requires all three filters; assigned-to must be a USER id."""
        response = await self._call(
            HOLIDAYS_LIST_IN_PERIOD,
            path={"workspaceId": self._workspace(workspace_id)},
            query={"assigned_to": assigned_to, "start": start, "end": end},
        )
        return self._adapt(HOLIDAYS_LIST_IN_PERIOD, response, _HOLIDAY_LIST)

    async def update(
        self,
        holiday_id: str,
        body: "UpdateHolidayRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> HolidayDto:
        """Full replacement; omitted fields 400. No single-GET route: list-scan first."""
        validated = self._coerce(body, UpdateHolidayRequest)
        response = await self._call(
            HOLIDAYS_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "holidayId": holiday_id},
            body=validated,
        )
        return self._adapt(HOLIDAYS_UPDATE, response, HolidayDto)
