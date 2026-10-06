---
description: Build JSON-RPC 2.0 requests in Python with request and request_json, with positional or named params and your own ids.
---

# Requests

## The request function

`request` builds a request as a dict:

```pycon
>>> from jsonrpcclient import request
>>> request("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
```

`request_json` gives the same request as a JSON string. It's `json.dumps`
applied to the result of `request`, and it uses the same id sequence:

```pycon
>>> from jsonrpcclient import request_json
>>> request_json("ping")
'{"jsonrpc": "2.0", "method": "ping", "id": 2}'
```

Most HTTP libraries serialize a dict for you (`json=` in requests, httpx and
aiohttp), so use `request` with those. Use `request_json` where you send text
yourself, as with websockets or ZeroMQ.

The ids in the examples on this page continue from one block to the next,
because each call takes the next id. [Ids](ids.md) explains how ids work and
how to choose your own.

## Parameters

Pass a list (or tuple) for positional parameters, or a dict for named ones:

```pycon
>>> request("sqrt", params=[16])
{'jsonrpc': '2.0', 'method': 'sqrt', 'params': [16], 'id': 3}
>>> request("sqrt", params=(16,))
{'jsonrpc': '2.0', 'method': 'sqrt', 'params': [16], 'id': 4}
>>> request("greet", params={"name": "Ada"})
{'jsonrpc': '2.0', 'method': 'greet', 'params': {'name': 'Ada'}, 'id': 5}
```

`params` is also the second positional argument, so `request("sqrt", [16])`
works too.

A tuple is sent as a list. Empty params (`[]`, `()`, `{}` or `None`) are left
out of the request, which JSON-RPC 2.0 allows. The library doesn't check the
type of `params` at runtime, but mypy and pyright flag anything other than a
list, tuple or dict.

!!! warning "A string is not params"
    `request("get", "fruit")` sends `"params": "fruit"`, which isn't valid
    JSON-RPC. Wrap a single positional argument in a list:
    `request("get", ["fruit"])`. This is also what happens to 3.x code that
    passes a URL first. See [Migration](migration.md).

## Your own id

Pass `id` to choose the id yourself. Any JSON value works:

```pycon
>>> request("ping", id="abc")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 'abc'}
```

`id=None` sends `"id": null`. That is still a request, not a
[notification](notifications.md), and JSON-RPC 2.0 discourages it.

## Other id styles

`request_hex`, `request_random` and `request_uuid` work like `request` but
generate hexadecimal, random or UUID ids. `request_json_hex`,
`request_json_random` and `request_json_uuid` are their JSON string versions.
See [Ids](ids.md).

## What to read next

- [Notifications](notifications.md), for calls that need no reply.
- [Batches](batches.md), to send several requests at once.
- [Responses](responses.md), to read the reply.
