---
description: Send JSON-RPC 2.0 requests over HTTP with httpx and jsonrpcclient, both synchronously and with asyncio.
---

# httpx

[httpx](https://www.python-httpx.org/) has the same `json=` and
`raise_for_status()` as requests, and adds an async client.

## Sync

```python
--8<-- "docs/examples/httpx_client.py"
```

## Async

```python
--8<-- "docs/examples/httpx_async.py"
```

`raise_for_status()` raises `httpx.HTTPStatusError` for a 4xx or 5xx status.
Connection problems and timeouts raise subclasses of `httpx.TransportError`.
For many calls, keep one `httpx.Client` or `httpx.AsyncClient` open and reuse
it.
