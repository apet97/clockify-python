"""Time entries resource: explicit methods over the time-entry operations."""

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import Field, TypeAdapter

from clockify.models import (
    BulkEditTimeEntryRequest,
    CreateTimeEntryRequest,
    GetTimeEntriesByIdsRequest,
    TimeEntriesTimeEntry,
    TimeEntry,
    TimeEntryCreate,
    TimeEntryDtoImplV1,
    TimeEntryUpdate,
    TimeEntryWithRatesDtoV1,
)
from clockify.models.base import ClockifyRequestModel
from clockify.operations.time_entries import (
    TIME_ENTRIES_BULK_UPDATE_FOR_USER,
    TIME_ENTRIES_CREATE,
    TIME_ENTRIES_CREATE_FOR_USER,
    TIME_ENTRIES_DELETE,
    TIME_ENTRIES_DELETE_ALL_FOR_USER,
    TIME_ENTRIES_DUPLICATE,
    TIME_ENTRIES_GET,
    TIME_ENTRIES_GET_MANY,
    TIME_ENTRIES_LIST_FOR_USER,
    TIME_ENTRIES_LIST_IN_PROGRESS,
    TIME_ENTRIES_MARK_INVOICED,
    TIME_ENTRIES_STOP_TIMER_FOR_USER,
    TIME_ENTRIES_UPDATE,
)
from clockify.resources._base import ResourceBase

_TIME_ENTRIES_LIST = TypeAdapter(list[TimeEntriesTimeEntry])
_TIME_ENTRY_LIST = TypeAdapter(list[TimeEntry])
_TIME_ENTRY_DTO_V1_LIST = TypeAdapter(list[TimeEntryDtoImplV1])
_TIME_ENTRY_WITH_RATES_LIST = TypeAdapter(list[TimeEntryWithRatesDtoV1])


class _MarkTimeEntriesInvoicedRequest(ClockifyRequestModel):
    invoiced: bool
    time_entry_ids: list[str] = Field(alias="timeEntryIds")


class _StopTimerRequest(ClockifyRequestModel):
    end: str


class TimeEntriesResource(ResourceBase):
    async def bulk_update_for_user(
        self,
        user_id: str,
        body: "Sequence[BulkEditTimeEntryRequest | Mapping[str, Any]]",
        *,
        workspace_id: str | None = None,
        hydrated: bool | None = None,
    ) -> list[TimeEntriesTimeEntry]:
        """Body is a bare JSON array; PUT may replace omitted fields — resend them."""
        items = [
            self._coerce(item, BulkEditTimeEntryRequest).model_dump(
                by_alias=True, exclude_unset=True, mode="json"
            )
            for item in body
        ]
        response = await self._call(
            TIME_ENTRIES_BULK_UPDATE_FOR_USER,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            query={"hydrated": hydrated},
            body=items,
        )
        return self._adapt(TIME_ENTRIES_BULK_UPDATE_FOR_USER, response, _TIME_ENTRIES_LIST)

    async def create(
        self,
        body: "CreateTimeEntryRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> TimeEntriesTimeEntry:
        """Custom-field write key is `customFields`; `customFieldValues` is silently dropped."""
        validated = self._coerce(body, CreateTimeEntryRequest)
        response = await self._call(
            TIME_ENTRIES_CREATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(TIME_ENTRIES_CREATE, response, TimeEntriesTimeEntry)

    async def create_for_user(
        self,
        user_id: str,
        body: "TimeEntryCreate | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
        from_entry: str | None = None,
    ) -> TimeEntry:
        """Custom-field write key is `customFields`; `customFieldValues` is silently dropped."""
        validated = self._coerce(body, TimeEntryCreate)
        response = await self._call(
            TIME_ENTRIES_CREATE_FOR_USER,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            query={"from_entry": from_entry},
            body=validated,
        )
        return self._adapt(TIME_ENTRIES_CREATE_FOR_USER, response, TimeEntry)

    async def delete(self, time_entry_id: str, *, workspace_id: str | None = None) -> None:
        await self._call(
            TIME_ENTRIES_DELETE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "timeEntryId": time_entry_id,
            },
        )
        return None

    async def delete_all_for_user(
        self,
        user_id: str,
        *,
        workspace_id: str | None = None,
        time_entry_ids: list[str],
    ) -> list[TimeEntryDtoImplV1]:
        """Multi-entity delete; `time-entry-ids` is a required repeated query key."""
        response = await self._call(
            TIME_ENTRIES_DELETE_ALL_FOR_USER,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            query={"time_entry_ids": time_entry_ids},
        )
        return self._adapt(TIME_ENTRIES_DELETE_ALL_FOR_USER, response, _TIME_ENTRY_DTO_V1_LIST)

    async def duplicate(
        self, user_id: str, time_entry_id: str, *, workspace_id: str | None = None
    ) -> TimeEntriesTimeEntry:
        response = await self._call(
            TIME_ENTRIES_DUPLICATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "userId": user_id,
                "timeEntryId": time_entry_id,
            },
        )
        return self._adapt(TIME_ENTRIES_DUPLICATE, response, TimeEntriesTimeEntry)

    async def get(
        self,
        time_entry_id: str,
        *,
        workspace_id: str | None = None,
        hydrated: bool | None = None,
        consider_duration_format: bool | None = None,
    ) -> TimeEntry:
        response = await self._call(
            TIME_ENTRIES_GET,
            path={
                "workspaceId": self._workspace(workspace_id),
                "timeEntryId": time_entry_id,
            },
            query={
                "hydrated": hydrated,
                "consider_duration_format": consider_duration_format,
            },
        )
        return self._adapt(TIME_ENTRIES_GET, response, TimeEntry)

    async def get_many(
        self,
        body: "GetTimeEntriesByIdsRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> list[TimeEntryWithRatesDtoV1]:
        """Non-mutating POST: batch read of time entries by id."""
        validated = self._coerce(body, GetTimeEntriesByIdsRequest)
        response = await self._call(
            TIME_ENTRIES_GET_MANY,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(TIME_ENTRIES_GET_MANY, response, _TIME_ENTRY_WITH_RATES_LIST)

    async def list_for_user(
        self,
        user_id: str,
        *,
        workspace_id: str | None = None,
        description: str | None = None,
        start: str | None = None,
        end: str | None = None,
        project: str | None = None,
        task: str | None = None,
        tags: list[str] | None = None,
        project_required: bool | None = None,
        task_required: bool | None = None,
        hydrated: bool | None = None,
        in_progress: bool | None = None,
        get_week_before: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[TimeEntry]:
        """`start`/`end` are re-read as wall clock in the account's timezone."""
        response = await self._call(
            TIME_ENTRIES_LIST_FOR_USER,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            query={
                "description": description,
                "start": start,
                "end": end,
                "project": project,
                "task": task,
                "tags": tags,
                "project_required": project_required,
                "task_required": task_required,
                "hydrated": hydrated,
                "in_progress": in_progress,
                "get_week_before": get_week_before,
                "page": page,
                "page_size": page_size,
            },
        )
        return self._adapt(TIME_ENTRIES_LIST_FOR_USER, response, _TIME_ENTRY_LIST)

    async def list_in_progress(
        self,
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[TimeEntriesTimeEntry]:
        response = await self._call(
            TIME_ENTRIES_LIST_IN_PROGRESS,
            path={"workspaceId": self._workspace(workspace_id)},
            query={"page": page, "page_size": page_size},
        )
        return self._adapt(TIME_ENTRIES_LIST_IN_PROGRESS, response, _TIME_ENTRIES_LIST)

    async def mark_invoiced(
        self,
        body: Mapping[str, Any],
        *,
        workspace_id: str | None = None,
    ) -> None:
        """Multi-entity financial transition: {invoiced: bool, timeEntryIds: [str]}."""
        validated = self._coerce(body, _MarkTimeEntriesInvoicedRequest)
        await self._call(
            TIME_ENTRIES_MARK_INVOICED,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return None

    async def stop_timer_for_user(
        self,
        user_id: str,
        body: Mapping[str, Any],
        *,
        workspace_id: str | None = None,
    ) -> TimeEntriesTimeEntry:
        """Body is {end: date-time}; this PATCH is the only stop-timer route."""
        validated = self._coerce(body, _StopTimerRequest)
        response = await self._call(
            TIME_ENTRIES_STOP_TIMER_FOR_USER,
            path={"workspaceId": self._workspace(workspace_id), "userId": user_id},
            body=validated,
        )
        return self._adapt(TIME_ENTRIES_STOP_TIMER_FOR_USER, response, TimeEntriesTimeEntry)

    async def update(
        self,
        time_entry_id: str,
        body: "TimeEntryUpdate | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> TimeEntry:
        """PUT may replace omitted fields — resend everything you want to keep."""
        validated = self._coerce(body, TimeEntryUpdate)
        response = await self._call(
            TIME_ENTRIES_UPDATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "timeEntryId": time_entry_id,
            },
            body=validated,
        )
        return self._adapt(TIME_ENTRIES_UPDATE, response, TimeEntry)
