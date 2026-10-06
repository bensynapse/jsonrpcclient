---
description: Send JSON-RPC 2.0 notifications in Python. A notification has no id, and the server doesn't reply to it.
---

# Notifications

A notification is a request without an id. The server runs it but doesn't
reply, so you can't find out whether it worked. Use it for fire-and-forget
calls such as logging.

```pycon
>>> from jsonrpcclient import notification, notification_json
>>> notification("log", ["hello"])
{'jsonrpc': '2.0', 'method': 'log', 'params': ['hello']}
>>> notification_json("log", ["hello"])
'{"jsonrpc": "2.0", "method": "log", "params": ["hello"]}'
```

Params work the same as for [requests](requests.md). Use a list or tuple for
positional params and a dict for named ones. Empty params are left out.

!!! note "Changed in 4.1.0"
    Tuple params in a notification are converted to a list, as `request`
    always did. The JSON is the same as before.

## Don't read a body

Because the server sends no JSON-RPC response, there's nothing to `parse`.
Over HTTP, servers usually answer with `204 No Content` or `200` and an empty
body. Calling `response.json()` on that raises a JSON decoding error, so check
the HTTP status and stop there:

<!-- requires: requests -->
<!-- server -->
```python
import requests

from jsonrpcclient import notification

response = requests.post(
    "http://localhost:8000/", json=notification("log", ["hello"]), timeout=10
)
response.raise_for_status()
print(response.status_code, response.content)
```

```text title="Output"
204 b''
```

Over a socket transport such as ZeroMQ's REQ/REP, check what your server does
before waiting for a reply that will never come.

## None is not a notification

`request("log", id=None)` is not a notification. It sends `"id": null`, and
the server replies to it. Use `notification` when you don't want a reply.
