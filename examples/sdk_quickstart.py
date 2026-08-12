"""Minimal SDK usage: reads, a guarded write, pagination, raw access."""

import asyncio
import os

from clockify import ClockifyClient, iter_all


async def main() -> None:
    async with ClockifyClient(
        api_key=os.environ["CLOCKIFY_API_KEY"],
        workspace_id=os.environ.get("CLOCKIFY_WORKSPACE_ID"),
    ) as clockify:
        me = await clockify.users.me()
        print("user:", me.name)

        projects = await clockify.projects.list(archived=False, page_size=25)
        print("projects on page 1:", [p.name for p in projects])

        # Explicit pagination with proven stop rules.
        async def fetch_page(page: int):
            from clockify import Page

            items = await clockify.tags.list(page=page, page_size=50)
            return Page(items=items, page=page, page_size=50, last_page=None)

        all_tags = await iter_all(fetch_page, max_pages=10)
        print("tags:", len(all_tags))

        # Full-replacement update: resend every field you must keep.
        # tag = await clockify.tags.update(tag_id, {"name": "x", "archived": False})

        # Bounded raw escape hatch (registered operation IDs only).
        raw = await clockify.raw.call(
            "getWorkspacesWorkspaceIdTags",
            path={"workspaceId": clockify.workspace_id or me.default_workspace},
            query={"page_size": 5},
        )
        print("raw last_page header:", raw.last_page)


asyncio.run(main())
