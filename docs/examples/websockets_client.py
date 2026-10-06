import asyncio
import logging

from websockets.asyncio.client import connect

from jsonrpcclient import Error, Ok, parse_json, request_json


async def main() -> None:
    async with connect("ws://localhost:5000") as websocket:
        await websocket.send(request_json("ping"))
        parsed = parse_json(await websocket.recv())
    if isinstance(parsed, Ok):
        print(parsed.result)
    elif isinstance(parsed, Error):
        logging.error(parsed.message)


asyncio.run(main())
