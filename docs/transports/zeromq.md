---
description: Send JSON-RPC 2.0 requests over ZeroMQ with pyzmq and jsonrpcclient.
---

# ZeroMQ

This uses a REQ socket from [pyzmq](https://pyzmq.readthedocs.io/). ZeroMQ
carries bytes, so use `request_json` and `parse_json`:

```python
--8<-- "docs/examples/zeromq_client.py"
```

A REQ socket must receive a reply after every send. Don't send a
[notification](../notifications.md) on one unless your server replies to
notifications with an empty message.
