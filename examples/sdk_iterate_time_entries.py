"""Iterate bounded pages of one user's time entries."""

import asyncio
import os

from pydantic import TypeAdapter

from clockify import ClockifyClient, Page, iter_all
from clockify.models import TimeEntry
from clockify.operations.time_entries import TIME_ENTRIES_LIST_FOR_USER

_TIME_ENTRIES = TypeAdapter(list[TimeEntry])


async def main() -> None:
    workspace_id = os.environ["CLOCKIFY_WORKSPACE_ID"]
    async with ClockifyClient(
        api_key=os.environ["CLOCKIFY_API_KEY"],
        workspace_id=workspace_id,
    ) as clockify:
        me = await clockify.users.me()

        async def fetch(page: int) -> Page[TimeEntry]:
            response = await clockify.raw.call(
                TIME_ENTRIES_LIST_FOR_USER.operation_id,
                path={"workspaceId": workspace_id, "userId": me.id},
                query={"page": page, "page_size": 50},
            )
            items = _TIME_ENTRIES.validate_python(response.data)
            return Page.from_response(response, items=items, page=page, page_size=50)

        entries = await iter_all(fetch, max_pages=20)
        print("time entries:", len(entries))


asyncio.run(main())
