---
title: Create JSON-RPC 2.0 requests and parse responses in Python
description: jsonrpcclient builds JSON-RPC 2.0 requests and parses the responses in Python. It works with any transport, has no dependencies, and is typed and thread-safe.
---

# jsonrpcclient

_Create JSON-RPC 2.0 requests and parse responses in Python._

jsonrpcclient builds [JSON-RPC 2.0](https://www.jsonrpc.org/specification)
requests and parses the responses. It doesn't send anything, so it works with
any transport: HTTP, websockets, ZeroMQ, or something of your own. It has no
dependencies, ships type hints, and is safe to use from several threads. It
supports Python 3.8 to 3.14, including free-threaded 3.14t.

## Install

```sh
pip install jsonrpcclient
```

## Quickstart

This sends `ping` to a JSON-RPC server at `http://localhost:8000/`, using
[requests](https://requests.readthedocs.io/) for the HTTP part:

```python
--8<-- "docs/examples/quickstart.py"
```

```text title="Output"
pong
```

`request` builds the request as a dict, and `parse` turns the reply into an
`Ok` or an `Error`:

```pycon
>>> from jsonrpcclient import parse, request
>>> request("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
>>> parse({"jsonrpc": "2.0", "result": "pong", "id": 1})
Ok(result='pong', id=1)
```

For JSON strings, use `request_json` and `parse_json`.

## Where next

- [Requests](requests.md), [notifications](notifications.md),
  [batches](batches.md) and [ids](ids.md): building what you send.
- [Responses](responses.md) and [error handling](errors.md): reading what
  comes back, and every way it can go wrong.
- [Transports](examples.md): complete examples with urllib, requests, httpx,
  aiohttp, websockets and ZeroMQ.
- [API reference](reference.md): every function and class, with signatures.
- [Typing](typing.md) and [threads and async](threads.md).
- [Migrating from 3.x](migration.md): the 4.x API is completely different.
- [jsonrpcserver](https://github.com/bensynapse/jsonrpcserver): the same
  idea for the server side.
