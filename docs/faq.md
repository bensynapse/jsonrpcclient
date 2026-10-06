# FAQ

## How do I use a different JSON library?

`request_json` is `json.dumps` applied after `request`, and `parse_json` is
`parse` applied after `json.loads`. You can build your own versions the same
way. This one uses [ujson](https://pypi.org/project/ujson/):

<!-- requires: ujson -->
```python
import ujson

from jsonrpcclient import parse, request
from jsonrpcclient.utils import compose

parse_json = compose(parse, ujson.loads)
request_json = compose(ujson.dumps, request)

print(request_json("ping"))
print(parse_json('{"jsonrpc": "2.0", "result": "pong", "id": 1}'))
```

## Is it thread-safe?

Yes, since 4.0.4. Every function can be called from several threads at once,
including on free-threaded Python (3.14t). If you use the generators in
`jsonrpcclient.id_generators` directly, those are safe to share too.

## Does it send requests?

No. It builds requests and parses responses. Use whatever HTTP, websocket or
socket library you like for the transport. See the [examples](examples.md).

## Where is the old documentation website?

The project's old website domain is no longer under the project's control, so
don't trust links to it. These pages are the official documentation now.
