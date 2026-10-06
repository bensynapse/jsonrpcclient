import asyncio
import logging

from aiohttp import ClientSession

from jsonrpcclient import Error, Ok, parse, request


async def main() -> None:
    async with ClientSession() as session, session.post(
        "http://localhost:5000/", json=request("ping")
    ) as response:
        parsed = parse(await response.json())
        if isinstance(parsed, Ok):
            print(parsed.result)
        elif isinstance(parsed, Error):
            logging.error(parsed.message)


asyncio.run(main())
