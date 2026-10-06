---
description: Send a batch of JSON-RPC 2.0 requests in Python and match the responses by id, including the edge cases that silently lose errors.
---

# Batches

A batch is a list of requests and notifications sent in one message. The
server replies with a list of responses, one for each request that has an id.

## Sending a batch

Build each request as usual and put them in a list:

```pycon
>>> import json
>>> from jsonrpcclient import notification, request
>>> json.dumps([request("ping", id=1), notification("log", ["hi"])])
'[{"jsonrpc": "2.0", "method": "ping", "id": 1}, {"jsonrpc": "2.0", "method": "log", "params": ["hi"]}]'
```

## Reading the responses

`parse` on a list gives an iterator of `Ok` and `Error`. The server can send
the responses in any order, so match them to your requests by id. This example
sends three requests and a notification to a test server that knows `ping`
and `add` but not `divide`:

<!-- requires: requests -->
<!-- server -->
```python
import requests

from jsonrpcclient import notification, parse, request

batch = [
    request("ping", id=1),
    request("add", [2, 3], id=2),
    request("divide", [1, 0], id=3),
    notification("log", ["hello"]),
]
response = requests.post("http://localhost:8000/", json=batch, timeout=10)
response.raise_for_status()
data = response.json()
if isinstance(data, dict):
    # The server rejected the whole batch. See "Edge cases" below.
    raise RuntimeError(f"Batch rejected: {parse(data)}")
by_id = {parsed.id: parsed for parsed in parse(data)}
for request_id in sorted(by_id):
    print(request_id, by_id[request_id])
```

```text title="Output"
1 Ok(result='pong', id=1)
2 Ok(result=5, id=2)
3 Error(code=-32601, message='Method not found', data=None, id=3)
```

The notification gets no response, so there are three, not four.

The iterator is lazy: each response is parsed when you reach it, and you can
go through it only once. Call `list()` on it, or build a dict as above, if
you need the responses more than once.

## Edge cases

These three cases catch people out. The [requests transport
example](transports/requests.md) handles the first one.

**The server rejects the whole batch.** The batch itself can be invalid, for
example an empty list. JSON-RPC 2.0 then has the server reply with a single
error object, not a list. `parse` on that dict returns one `Error`. Looping
over an `Error` goes through its fields (code, message, data, id). A loop
that checks `isinstance(parsed, Ok)` matches nothing and silently loses the
error, and one that reads `parsed.id` fails with `AttributeError`. Check the shape first:

```pycon
>>> from jsonrpcclient import parse
>>> data = {
...     "jsonrpc": "2.0",
...     "error": {"code": -32600, "message": "Invalid Request"},
...     "id": None,
... }
>>> isinstance(data, dict)
True
>>> parse(data)
Error(code=-32600, message='Invalid Request', data=None, id=None)
```

**A batch of only notifications gets no response at all.** Over HTTP that
is usually `204 No Content` with an empty body, so don't call
`response.json()` on it.

**Some errors come back with `"id": null`.** If the server can't read an
item's id, for example because the item isn't a valid request, it replies
with `"id": null`. In a dict keyed by id, those errors all collect under
`None`, and the request they belong to has no entry:

```pycon
>>> responses = parse(
...     [
...         {"jsonrpc": "2.0", "result": "pong", "id": 1},
...         {
...             "jsonrpc": "2.0",
...             "error": {"code": -32600, "message": "Invalid Request"},
...             "id": None,
...         },
...     ]
... )
>>> by_id = {parsed.id: parsed for parsed in responses}
>>> by_id[None]
Error(code=-32600, message='Invalid Request', data=None, id=None)
```

Check for a missing id when you look up your requests' responses.

## Invalid responses in a batch

If one item in a batch response is malformed, `parse` raises
`InvalidResponse` when the iterator reaches that item. The items before it
have already been returned. See [Error handling](errors.md).
