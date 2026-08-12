"""Read safe, bounded diagnostic fields from SDK errors."""

import asyncio
import os

from clockify import ClockifyAPIError, ClockifyClient, ClockifyTransportError


async def main() -> None:
    try:
        async with ClockifyClient(api_key=os.environ["CLOCKIFY_API_KEY"]) as clockify:
            await clockify.users.me()
    except ClockifyAPIError as error:
        print(error.operation_id, error.status_code, error.request_id, error.api_code)
        print(error.detail)
    except ClockifyTransportError as error:
        print(error.operation_id, str(error))


asyncio.run(main())
