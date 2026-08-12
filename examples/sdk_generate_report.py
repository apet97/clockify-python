"""Generate a summary report through the reports host."""

import asyncio
import os

from clockify import ClockifyClient


async def main() -> None:
    async with ClockifyClient(
        api_key=os.environ["CLOCKIFY_API_KEY"],
        workspace_id=os.environ.get("CLOCKIFY_WORKSPACE_ID"),
    ) as clockify:
        report = await clockify.reports.summary(
            {
                "dateRangeStart": "2026-08-01T00:00:00Z",
                "dateRangeEnd": "2026-08-08T00:00:00Z",
                "summaryFilter": {"groups": ["USER"]},
            }
        )
        print(report.model_dump_json(indent=2))


asyncio.run(main())
