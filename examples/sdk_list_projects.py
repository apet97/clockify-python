"""Read the current user and the first page of active projects."""

import asyncio
import os

from clockify import ClockifyClient


async def main() -> None:
    async with ClockifyClient(
        api_key=os.environ["CLOCKIFY_API_KEY"],
        workspace_id=os.environ.get("CLOCKIFY_WORKSPACE_ID"),
    ) as clockify:
        me = await clockify.users.me()
        projects = await clockify.projects.list(archived=False, page_size=25)
        print("user:", me.name)
        print("active projects:", [project.name for project in projects])


asyncio.run(main())
