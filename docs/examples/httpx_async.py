import asyncio
import logging

import httpx

from jsonrpcclient import Error, Ok, parse, request


async def main() -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post("http://localhost:8000/", json=request("ping"))
    response.raise_for_status()
    parsed = parse(response.json())
    if isinstance(parsed, Ok):
        print(parsed.result)
    elif isinstance(parsed, Error):
        logging.error(parsed.message)


asyncio.run(main())
