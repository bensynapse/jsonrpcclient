---
description: Upgrade jsonrpcclient from 4.x to 5.0, from 3.x to 4.x, and from 4.0 to 4.1. Every 5.0 change with its replacement, side-by-side examples, and the request(url, method) pitfall.
---

# Migration

## From 4.x to 5.0

Code that builds requests with `request` or `notification`, sends them, and
reads one response with `parse` or `parse_json` keeps working. A test in the
repository pins that. The rest of this section lists every change, so you can
check your own code against it.

Upgrade to 4.2.0 first and run your tests. It gives a `FutureWarning` for the
changes it can detect: a bad `method` or `params`, `parse_json(strict=...)`,
and an old Python. The two changes it can't detect are marked below.

### Python 3.11 or later

5.0 needs Python 3.11 or later. 3.8, 3.9 and 3.10 have reached end of life.
On an older Python, `pip install jsonrpcclient` keeps installing 4.x.

### Batches are lists

`parse` on a list, and `parse_json` on a JSON array, return a `list` of `Ok`
and `Error`. 4.x returned a lazy iterator.

| 4.x | 5.0 |
|---|---|
| `next(parse(batch))` | `parse(batch)[0]`, or `next(iter(parse(batch)))` |
| `list(parse(batch))` to read it twice | `parse(batch)`, which can be read as often as you like |
| a bad item raises when the loop reaches it, after the items before it | `parse` raises before it returns, and the message gives the index |
| `Iterator[Response]` in type hints | `list[Response]` |

Loops, `list()` and dict comprehensions over the result work as before.
4.2.0 can't warn about `next()` on a batch, so search your code for it.

### InvalidResponse is a ValueError

`InvalidResponse` subclasses `ValueError`. In 4.1 and 4.2 it subclassed
`KeyError` and `TypeError`, which 4.0 raised for a malformed response.

| 4.x | 5.0 |
|---|---|
| `except KeyError:` around `parse` | `except InvalidResponse:` |
| `except TypeError:` around `parse` | `except InvalidResponse:`. A str or bytes passed to `parse` still raises `TypeError` |
| `except (ValueError, InvalidResponse):` around `parse_json` | `except ValueError:` catches both |

4.2.0 can't warn about this either. Search for `except KeyError` and
`except TypeError` near `parse` and `parse_json`.

### Requests check method and params

`request`, `notification` and their variants raise `TypeError` when `method`
isn't a string, or `params` isn't a list, tuple, dict or None. 4.x sent the
request anyway, and the server rejected it.

| 4.x | 5.0 |
|---|---|
| `request("sqrt", "16")` sent `"params": "16"` | `TypeError`. Use `request("sqrt", [16])` |
| `request("get", "")` or `request("get", 0)` sent no params | `TypeError`. Leave `params` out, or pass `None` |
| `request(123)` sent `"method": 123` | `TypeError`. Use a string |

A rejected request uses up no id.

### Requests are TypedDicts

The request functions are typed as returning `Request`, and `notification`
as returning `Notification`. At run time they're the same dicts as before.
This only affects type checking.

| 4.x | 5.0 |
|---|---|
| `req: dict[str, Any] = request("ping")` | `req: Request = request("ping")`, or `Mapping[str, Any]` |
| `batch: list[dict[str, Any]] = [request(...), notification(...)]` | `batch: list[Request \| Notification] = [...]` |
| `request(...)["params"]` | `request(...).get("params")`, since `params` is left out when empty |
| `req["extra"] = 1` | a type error. Copy it into a `dict` first: `{**req, "extra": 1}` |

### parse_json's strict keyword

| 4.x | 5.0 |
|---|---|
| `parse_json(text, strict=False)` passed `strict` to `json.loads`, which then allowed control characters in strings | `parse(json.loads(text, strict=False))` |
| `parse_json(text, strict=True)`, the `json.loads` default | leave it out. `strict=True` now turns on the strict mode below |

Other keyword arguments, such as `parse_float`, still go to `json.loads`.

### New

- `match_responses(batch, parse(reply))` matches a batch's responses to its
  requests by id. See [Batches](batches.md#reading-the-responses).
- `parse(..., strict=True)` checks every JSON-RPC 2.0 rule for a response.
  See [Responses](responses.md#strict-mode).
- `Request` and `Notification` types. See [Typing](typing.md#requests-are-typeddicts).

## From 3.x to 4.x

Version 4 is a rewrite. In 3.x, jsonrpcclient sent the request over HTTP (or
another transport) for you. In 4.x it only builds the request and parses the
response, and you send it with any library you like.

!!! danger "Old calls fail silently on 4.x"
    In 3.x, `request("http://fruits.com", "get")` sent `get` to that URL. From
    4.x the first argument is the method name and the second is `params`. On
    4.x the same call returns a dict, sends nothing, and raises no error (4.2.0
    adds a `FutureWarning`). 5.0 raises `TypeError`, since `"get"` isn't valid
    params:

    ```pycon
    >>> from jsonrpcclient import request
    >>> request("http://fruits.com", "get")
    Traceback (most recent call last):
        ...
    TypeError: params must be a list, tuple or dict, not str
    ```

    If your code still calls `request` with a URL first, nothing reaches the
    server. Search your code for those calls when you upgrade. `notify` and
    `send` no longer exist, so code that uses them fails at import. With keyword arguments, such as `request(url, "get", color="yellow")`,
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

**A broken `error` next to a `result` now raises.** If a response has a
`result` and a non-null `error` that isn't an object with `code` and
`message`, such as `"error": "boom"` or `"error": false`, `parse` raises
`InvalidResponse`. 4.0 returned `Ok` and ignored the error. If a server you
use does this, catch `InvalidResponse` around `parse`.

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

**An empty response batch raises.** `parse([])` and `parse_json("[]")` raise
`InvalidResponse`. 4.0 returned an empty iterator. A batch response is never
empty: a server that has nothing to say for a batch of notifications sends no
response at all.

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
