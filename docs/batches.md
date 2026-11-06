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

`parse` on a list gives a list of `Ok` and `Error`. The server can send
the responses in any order. `match_responses` matches them to your requests
by id, and handles the edge cases below. This example sends three requests
and a notification to a test server that knows `ping` and `add` but not
`divide`:

<!-- requires: requests -->
<!-- server -->
```python
import requests

from jsonrpcclient import match_responses, notification, parse, request

batch = [
    request("ping", id=1),
    request("add", [2, 3], id=2),
    request("divide", [1, 0], id=3),
    notification("log", ["hello"]),
]
response = requests.post("http://localhost:8000/", json=batch, timeout=10)
response.raise_for_status()
matched = match_responses(batch, parse(response.json()))
for request_id, parsed in matched.items():
    print(request_id, parsed)
```

```text title="Output"
1 Ok(result='pong', id=1)
2 Ok(result=5, id=2)
3 Error(code=-32601, message='Method not found', data=None, id=3)
```

The notification gets no response, so there are three, not four. The dict
follows the order of the requests, whatever order the server used.

`parse` checks every response in the batch before it returns, and the list
can be read as often as you like.

!!! info "Changed in 5.0"
    4.x returned a lazy iterator, which could be read only once and raised
    for a bad item only when the loop reached it. `match_responses` is new
    in 5.0.

## What match_responses checks

- **A rejected batch.** If the server sends one error instead of a list,
  every request gets that error.
- **Errors with a null id.** A request with no response of its own gets one
  of those, in order. Left-over ones belong to notifications.
- **Anything it can't match** raises `InvalidResponse`: a request with no
  response, a response for an id you didn't send, two responses for one id,
  or a single `Ok` for a batch.
- **Two requests with the same id** raise `ValueError`, since their responses
  can't be told apart.

```pycon
>>> from jsonrpcclient import Error, Ok, match_responses, request
>>> batch = [request("ping", id=1), request("ping", id=2)]
>>> match_responses(batch, Error(-32600, "Invalid Request", None, None))
{1: Error(code=-32600, message='Invalid Request', data=None, id=None), 2: Error(code=-32600, message='Invalid Request', data=None, id=None)}
>>> match_responses(batch, [Ok("pong", 1)])
Traceback (most recent call last):
    ...
jsonrpcclient.responses.InvalidResponse: Invalid JSON-RPC response: no response for id 2
```

## Edge cases

These three cases catch people out if you match responses yourself.
`match_responses` handles all three. The [requests transport
example](transports/requests.md) handles the first one by hand.

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

An empty response array is invalid under
[JSON-RPC 2.0](https://www.jsonrpc.org/specification#batch).
`parse([])` and `parse_json("[]")` raise `InvalidResponse` immediately:

```pycon
>>> parse([])
Traceback (most recent call last):
    ...
jsonrpcclient.responses.InvalidResponse: Invalid JSON-RPC response: batch must not be empty
```

If one item in a batch response is malformed, `parse` raises
`InvalidResponse` before it returns anything, and the message gives the
index of the bad item. See [Error handling](errors.md).
