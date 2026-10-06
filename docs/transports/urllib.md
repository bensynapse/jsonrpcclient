---
description: Send JSON-RPC 2.0 requests over HTTP with Python's standard library urllib and jsonrpcclient, with no other dependencies.
---

# urllib

`urllib.request` is in the standard library, so this example needs nothing
but jsonrpcclient. It sends the request as a JSON string and parses the bytes
that come back:

```python
--8<-- "docs/examples/urllib_client.py"
```

`urlopen` raises `urllib.error.HTTPError` for an HTTP error status and
`urllib.error.URLError` if it can't connect. Both are `OSError` subclasses.

For a batch, send `json.dumps([request(...), ...])` and handle the reply as
shown in [Batches](../batches.md).
