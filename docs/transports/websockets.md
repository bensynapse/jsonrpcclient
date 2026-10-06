---
description: Send JSON-RPC 2.0 requests over a WebSocket with the websockets library and jsonrpcclient.
---

# websockets

A WebSocket carries text, so use `request_json` and `parse_json`. This uses
the `websockets.asyncio` client from
[websockets](https://websockets.readthedocs.io/) 13 and later:

```python
--8<-- "docs/examples/websockets_client.py"
```

A WebSocket connection can carry many requests at once, and the server may
answer them in any order. If you send several before reading, match the
replies to your requests by id.
