"""Iterate bounded pages of one user's time entries."""

import asyncio
import os

from clockify import ClockifyClient, Page, iter_all
from clockify.models import TimeEntry


async def main() -> None:
    async with ClockifyClient(
        api_key=os.environ["CLOCKIFY_API_KEY"],
        workspace_id=os.environ.get("CLOCKIFY_WORKSPACE_ID"),
    ) as clockify:
        me = await clockify.users.me()

        async def fetch(page: int) -> Page[TimeEntry]:
            items = await clockify.time_entries.list_for_user(
                me.id,
                page=page,
                page_size=50,
            )
            return Page(items=items, page=page, page_size=50, last_page=None)

        entries = await iter_all(fetch, max_pages=20)
        print("time entries:", len(entries))


asyncio.run(main())
