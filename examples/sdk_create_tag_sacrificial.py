"""Create and remove one uniquely named tag in a verified sacrificial workspace."""

import asyncio
import os
import uuid

from clockify import ClockifyClient


async def main() -> None:
    if os.environ.get("CLOCKIFY_SACRIFICIAL_CONFIRM") != "yes":
        raise RuntimeError("set CLOCKIFY_SACRIFICIAL_CONFIRM=yes after workspace verification")

    name = f"py115-example-{uuid.uuid4().hex}"
    created_id: str | None = None
    async with ClockifyClient(
        api_key=os.environ["CLOCKIFY_API_KEY"],
        workspace_id=os.environ["CLOCKIFY_WORKSPACE_ID"],
    ) as clockify:
        try:
            tag = await clockify.tags.create({"name": name})
            created_id = tag.id
            print("created tag id:", created_id)
        finally:
            if created_id is not None:
                await clockify.tags.delete(created_id)

    # Clockify can reserve a deleted tag name. A later run must use a new name.


asyncio.run(main())
