---
description: Every way a JSON-RPC call can fail in Python, and how to catch each one with jsonrpcclient and your transport library.
---

# Error handling

A JSON-RPC call can go wrong in several places. jsonrpcclient handles the last
part, reading the response. Your transport library handles the rest.

## What can go wrong

| What happened | What you get | How to handle it |
|---|---|---|
| Can't connect, or the request timed out | your transport's exception, such as `requests.ConnectionError`, `requests.Timeout`, `httpx.TransportError`, `aiohttp.ClientConnectionError` or `urllib.error.URLError` | catch it around the call |
| The server sent an HTTP error status (4xx or 5xx) | nothing, unless you ask: requests and httpx need `response.raise_for_status()`, aiohttp needs `ClientSession(raise_for_status=True)`. urllib raises `HTTPError` by itself | call `raise_for_status()` before parsing |
| The body isn't JSON, such as an HTML error page or an empty body | `requests.JSONDecodeError`, `json.JSONDecodeError` from `parse_json` or httpx, or `aiohttp.ContentTypeError`. All but the last are `ValueError` subclasses | catch `ValueError` (and `ContentTypeError` with aiohttp) |
| The server ran the method and it failed | an `Error` from `parse` | check with `isinstance` or `match` |
| The JSON isn't a valid JSON-RPC response | `InvalidResponse` | catch `InvalidResponse` |
| The server rejected a whole batch | one `Error` instead of an iterator | check `isinstance(data, dict)`, see [Batches](batches.md#edge-cases) |
| The request was a notification | no body at all | don't parse, see [Notifications](notifications.md) |

## A complete example

This wraps a call in a function that returns the result or raises. A
JSON-RPC error becomes a Python exception of your own:

<!-- requires: requests -->
<!-- server -->
```python
from typing import Any, Optional

import requests

from jsonrpcclient import Error, parse, request


class RPCError(Exception):
    def __init__(self, error: Error) -> None:
        super().__init__(f"{error.message} (code {error.code})")
        self.error = error


def call(method: str, params: Optional[list] = None) -> Any:
    response = requests.post(
        "http://localhost:8000/", json=request(method, params), timeout=10
    )
    response.raise_for_status()  # HTTP errors: requests.HTTPError
    parsed = parse(response.json())  # Not JSON: requests.JSONDecodeError
    if isinstance(parsed, Error):
        raise RPCError(parsed)
    return parsed.result


print(call("add", [2, 3]))
try:
    call("divide", [1, 0])
except RPCError as exc:
    print("RPC error:", exc)
```

```text title="Output"
5
RPC error: Method not found (code -32601)
```

`parse` raises `InvalidResponse` if the reply is malformed. It's left to
propagate here, since there's nothing useful to do with a broken reply except
report it.

## HTTP errors

Without `raise_for_status()`, an HTTP error page goes straight to
`response.json()`, which fails with a less helpful error:

<!-- requires: requests -->
<!-- server -->
```python
import requests

from jsonrpcclient import parse, request

response = requests.post(
    "http://localhost:8000/wrong-path", json=request("ping"), timeout=10
)
try:
    parse(response.json())
except ValueError as exc:
    print(type(exc).__name__)

try:
    response.raise_for_status()
except requests.HTTPError as exc:
    print("HTTP error:", exc.response.status_code)
```

```text title="Output"
JSONDecodeError
HTTP error: 404
```

Some servers send JSON-RPC errors with an HTTP error status, such as 500. If
yours does, read the body before calling `raise_for_status()`, or parse it in
your `except` block.

## InvalidResponse

`InvalidResponse` means the server sent JSON that isn't a JSON-RPC 2.0
response. Perhaps it has no `id`, or neither `result` nor `error`. Perhaps
its `error` isn't an object with `code` and `message`, or the value isn't an
object at all. The message says which.

!!! info "New in 4.1.0"
    Earlier versions raised a plain `KeyError` or `TypeError` here.
    `InvalidResponse` subclasses both, so old `except KeyError` and
    `except TypeError` clauses still catch it.

`parse` also raises a plain `TypeError` if you pass it a string or bytes.
That's a bug in the calling code, not a bad response, so it isn't an
`InvalidResponse`. Use `parse_json` for strings.

## Responses from servers you don't trust

The library checks the shape of a response, not its size or content.

- **Size.** There's no size limit. Limit the response size in your transport
  if the server isn't trusted.
- **Deep nesting.** Very deeply nested JSON raises `RecursionError` from
  `json.loads`.
- **Huge integers.** An integer with more than 4,300 digits raises
  `ValueError` on Python 3.11 and later. The 3.8.14, 3.9.14 and 3.10.7
  security releases added the same limit.
- **NaN and Infinity.** Python's `json` module accepts `NaN`, `Infinity` and
  `-Infinity`, which aren't valid JSON. To reject them, pass `parse_constant`
  to `parse_json`:

```pycon
>>> from jsonrpcclient import parse_json
>>> parse_json('{"jsonrpc": "2.0", "result": NaN, "id": 1}')
Ok(result=nan, id=1)
>>> def reject(name):
...     raise ValueError(f"invalid JSON constant {name}")
>>> parse_json('{"jsonrpc": "2.0", "result": NaN, "id": 1}', parse_constant=reject)
Traceback (most recent call last):
    ...
ValueError: invalid JSON constant NaN
```

`result` and `data` can be any JSON value. Validate them before you use them,
as you would any other input from the network.
