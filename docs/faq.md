---
description: Answers to common jsonrpcclient questions, including other JSON libraries, why it doesn't send requests, batch loops that print nothing, and the old website domains.
---

# FAQ

## Why doesn't it send requests?

Because every project already has a way to talk to its server, and they all
differ. Some use requests and some httpx, some are async, and each has its
own retries, timeouts and authentication. jsonrpcclient handles the JSON-RPC
part and leaves the transport to you, which is also why it has no
dependencies. [Transports](examples.md) has a complete example for each
common library.

## How do I use a different JSON library?

`request_json` is `json.dumps` applied after `request`, and `parse_json` is
`parse` applied after `json.loads`. You can build your own versions the same
way with `compose`. This one uses [ujson](https://pypi.org/project/ujson/):

<!-- requires: ujson -->
```python
import ujson

from jsonrpcclient import parse, request
from jsonrpcclient.utils import compose

parse_json = compose(parse, ujson.loads)
request_json = compose(ujson.dumps, request)

print(request_json("ping"))
print(parse_json('{"jsonrpc":"2.0","result":"pong","id":1}'))
```

```text title="Output"
{"jsonrpc":"2.0","method":"ping","id":1}
Ok(result='pong', id=1)
```

[orjson](https://pypi.org/project/orjson/) works the same way, but its
`dumps` returns bytes, not a string. Most transports accept bytes, so that's
usually fine.

## The server sends both result and error. What do I get?

An `Error`, if `error` is an object and not null. See
[Responses](responses.md#a-response-with-both-result-and-error). This
changed in 4.1.0.

## My batch loop prints nothing

The server probably rejected the whole batch. It then sends a single error
object instead of a list, and looping over the `Error` that `parse` returns
goes through its fields without matching `Ok` or `Error`. Check
`isinstance(data, dict)` before looping. See [Batches](batches.md#edge-cases).

## Why does mypy say Error has no attribute result?

Because `parse` may return an `Error`, which has no `result`. Check with
`isinstance` or `match` first. See [Typing](typing.md).

## Is it thread-safe?

Yes, including on free-threaded Python. See [Threads and
async](threads.md).

## Where is the command-line tool?

The `jsonrpc` command from 2.x and 3.x was removed in 4.0.0. To try a server
from the shell, build the request with Python and send it with curl:

```sh
python -c 'from jsonrpcclient import request_json; print(request_json("ping"))' \
  | curl -s -H 'Content-Type: application/json' --data @- http://localhost:8000/
```

## I'm upgrading from 3.x

See [Migration](migration.md). Calls written for 3.x, such as
`request("http://example.com", "get")`, still run on 4.x but send nothing.

## Where is the old documentation website?

The project's old domains, jsonrpcclient.com and jsonrpcserver.com, now
belong to someone else. Ignore them and any links to them. The copy at
explodinglabs.com/jsonrpcclient/ is old and no longer updated.

The official places are these docs, the [GitHub
repository](https://github.com/bensynapse/jsonrpcclient) and the [PyPI
project](https://pypi.org/project/jsonrpcclient/).
