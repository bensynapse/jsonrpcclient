---
description: Use jsonrpcclient with any transport. Complete, tested examples with urllib, requests, httpx, aiohttp, websockets and ZeroMQ.
---

# Transports

jsonrpcclient only builds requests and parses responses, so you pair it with a
library that sends them. Each page below has a complete example that talks to
a JSON-RPC server on `localhost:8000` that answers `ping` with `pong`. CI runs
every one of them against a test server.

| Transport | Library | Sync or async | Page |
|---|---|---|---|
| HTTP | `urllib` (standard library, no install) | sync | [urllib](transports/urllib.md) |
| HTTP | [requests](https://requests.readthedocs.io/) | sync | [requests](transports/requests.md) |
| HTTP | [httpx](https://www.python-httpx.org/) | both | [httpx](transports/httpx.md) |
| HTTP | [aiohttp](https://docs.aiohttp.org/) | async | [aiohttp](transports/aiohttp.md) |
| WebSocket | [websockets](https://websockets.readthedocs.io/) | async | [websockets](transports/websockets.md) |
| ZeroMQ | [pyzmq](https://pyzmq.readthedocs.io/) | sync | [ZeroMQ](transports/zeromq.md) |

The pattern is the same everywhere:

1. Build the request with `request` (or `request_json` if the library sends
   text).
2. Send it, and check for transport errors such as an HTTP error status.
3. Parse the reply with `parse` (or `parse_json` for text), then check
   whether you got an `Ok` or an `Error`.

[Error handling](errors.md) lists what can go wrong at each step.

!!! tip "Port 8000"
    The examples use port 8000. Port 5000, which many tutorials use, is taken
    by the AirPlay Receiver on recent macOS versions.
