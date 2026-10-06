---
description: Send JSON-RPC 2.0 requests and batches over HTTP with the requests library and jsonrpcclient, with error handling.
---

# requests

[requests](https://requests.readthedocs.io/) serializes the dict that
`request` returns when you pass it as `json=`:

```python
--8<-- "docs/examples/requests_client.py"
```

`raise_for_status()` raises `requests.HTTPError` for a 4xx or 5xx status.
Without it, an HTML error page reaches `response.json()` and fails with
`requests.JSONDecodeError`.

## A batch

Send a list of requests, then check the shape of the reply before looping.
A server that rejects the whole batch sends one error object instead of a
list:

```python
--8<-- "docs/examples/requests_batch.py"
```

[Batches](../batches.md) explains this and the other edge cases.

## Reusing a connection

For many calls, use a `requests.Session` so the connection stays open:

<!-- requires: requests -->
<!-- server -->
```python
import requests

from jsonrpcclient import Error, Ok, parse, request

with requests.Session() as session:
    for _ in range(2):
        response = session.post(
            "http://localhost:8000/", json=request("ping"), timeout=10
        )
        response.raise_for_status()
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            print(parsed.result)
        elif isinstance(parsed, Error):
            print("Error:", parsed.message)
```

```text title="Output"
pong
pong
```
