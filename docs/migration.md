---
description: Upgrade jsonrpcclient from 3.x to 4.x, and from 4.0 to 4.1. Side-by-side examples, removed features, and the silent request(url, method) pitfall.
---

# Migration

## From 3.x to 4.x

Version 4 is a rewrite. In 3.x, jsonrpcclient sent the request over HTTP (or
another transport) for you. In 4.x it only builds the request and parses the
response, and you send it with any library you like.

!!! danger "Old calls can fail silently"
    In 3.x, `request("http://fruits.com", "get")` sent `get` to that URL. In
    4.x the first argument is the method name and the second is `params`. So
    the same call returns a dict, sends nothing, and raises no error:

    ```pycon
    >>> from jsonrpcclient import request
    >>> request("http://fruits.com", "get")
    {'jsonrpc': '2.0', 'method': 'http://fruits.com', 'params': 'get', 'id': 1}
    ```

    If your code still calls `request`, `notify` or `send` with a URL first,
    nothing reaches the server. Search your code for those calls when you
    upgrade. With keyword arguments, such as `request(url, "get", color="yellow")`,
    you get `TypeError: request() got an unexpected keyword argument 'color'`
    instead.

### A request, before and after

3.x:

<!-- skip: 3.x code -->
```python
# jsonrpcclient 3.x. This doesn't run on 4.x.
from jsonrpcclient import request

response = request("http://localhost:8000/", "get", color="yellow")
print(response.data.result)
```

4.x, using [requests](https://requests.readthedocs.io/) to send it:

<!-- requires: requests -->
<!-- server -->
```python
import requests

from jsonrpcclient import Error, Ok, parse, request

response = requests.post(
    "http://localhost:8000/", json=request("add", [2, 3]), timeout=10
)
response.raise_for_status()
parsed = parse(response.json())
if isinstance(parsed, Ok):
    print(parsed.result)
elif isinstance(parsed, Error):
    print("Error:", parsed.message)
```

```text title="Output"
5
```

Keyword arguments become a dict: `request("get", {"color": "yellow"})`.
Positional arguments become a list: `request("add", [2, 3])`.

### What changed

| 3.x | 4.x |
|---|---|
| `request(url, method, *args, **kwargs)` sends a request | `request(method, params)` returns a dict, and you send it |
| `notify(url, method, ...)` | `notification(method, params)`, then send it |
| `send(url, request)` | send the request with your HTTP library |
| `HTTPClient(url).request(...)`, `.notify(...)`, `.send(...)` | [requests](transports/requests.md), [httpx](transports/httpx.md) or [urllib](transports/urllib.md) |
| `jsonrpcclient.clients.*` (aiohttp, tornado, websockets, zeromq, socket) | the library itself, as in [Transports](examples.md) |
| `client.some_method(...)` attribute calls | `request("some_method", ...)` |
| `Request("ping")` and `Notification("ping")` classes | the `request` and `notification` functions |
| `response.data.result` | `parse(...).result`, after checking you got an `Ok` |
| `response.data.ok` | `isinstance(parsed, Ok)` |
| `ReceivedErrorResponseError` raised on an error response | `parse` returns an `Error`. Raise your own exception if you want one, as in [Error handling](errors.md#a-complete-example) |
| `ReceivedNon2xxResponseError` | your HTTP library, such as `response.raise_for_status()` |
| jsonschema validation of responses | `parse` checks the response shape and raises `InvalidResponse` (4.1.0 and later) |
| logging of requests and responses | log the request dict and the reply yourself |
| the `jsonrpc` command-line tool | removed, see the [FAQ](faq.md#where-is-the-command-line-tool) |
| `pip install "jsonrpcclient[requests]"` extras | `pip install jsonrpcclient requests` (there are no extras) |

The 3.x documentation is no longer online. The [changelog](changelog.md)
lists every 3.x change.

## From 4.0 to 4.1

Most code needs no change. These are the differences you might notice.

**A response with both `result` and `error` is now an `Error`.** If `error`
is present and not null, `parse` returns an `Error`. 4.0 returned
`Ok(result=None)` and dropped the server's error. If you relied on that, check
for `Error` instead.

**Malformed responses raise `InvalidResponse`.** It subclasses `KeyError` and
`TypeError`, which 4.0 raised, so existing `except KeyError` or
`except TypeError` clauses still work. You can now catch `InvalidResponse`
directly:

```python
from jsonrpcclient import InvalidResponse, parse

try:
    parse({"jsonrpc": "2.0", "result": "pong"})
except InvalidResponse as exc:
    print(exc)
```

```text title="Output"
Invalid JSON-RPC response: missing 'id'
```

**New error messages.** `parse_json('"pong"')` used to say "Use parse_json on
strings". It now says it expected an object. Update any test that matches the
old text.

**`parse` on bytes** now raises `TypeError: Use parse_json on strings`, the
same as for a str.

**Tuple params in notifications** are now sent as a list. The JSON is the
same, but the dict that `notification` returns holds a list.

**Type hints (4.0.4).** `parse` has overloads and `parse_json` is no longer
typed as `Any`. Code that uses `parse_json(...).result` without an
`isinstance` check now fails mypy. See [Typing](typing.md).

**Python 3.8 or later (4.0.4).** Python 3.6 and 3.7 keep installing 4.0.3.
