---
description: Send JSON-RPC 2.0 requests over HTTP with aiohttp and jsonrpcclient in asyncio code.
---

# aiohttp

[aiohttp](https://docs.aiohttp.org/) is an asyncio HTTP client:

```python
--8<-- "docs/examples/aiohttp_client.py"
```

With `raise_for_status=True`, aiohttp raises `aiohttp.ClientResponseError` for
a 4xx or 5xx status. `response.json()` raises `aiohttp.ContentTypeError` if
the server doesn't label the body as JSON. Pass `content_type=None` to skip
that check for a server that sends JSON with the wrong content type.
