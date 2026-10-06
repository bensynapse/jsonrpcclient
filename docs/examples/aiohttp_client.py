import asyncio
import logging

from aiohttp import ClientSession

from jsonrpcclient import Error, Ok, parse, request


async def main() -> None:
    # raise_for_status=True raises aiohttp.ClientResponseError for 4xx and 5xx.
    async with ClientSession(raise_for_status=True) as session, session.post(
        "http://localhost:8000/", json=request("ping")
    ) as response:
        parsed = parse(await response.json())
    if isinstance(parsed, Ok):
        print(parsed.result)
    elif isinstance(parsed, Error):
        logging.error(parsed.message)


asyncio.run(main())
