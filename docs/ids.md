---
description: How jsonrpcclient picks JSON-RPC request ids, how to choose your own, and which id style to use with threads and several processes.
---

# Ids

Every request has an id, and the server copies it into the response. That is
how you match a response to its request, which matters most for
[batches](batches.md).

## The four id styles

| Function | Ids | Example |
|---|---|---|
| `request` | integers counting up from 1 | `1`, `2`, `3` |
| `request_hex` | hexadecimal strings counting up from "1" | `"9"`, `"a"`, `"b"` |
| `request_random` | 8 random lowercase letters and digits | `"fubui5e6"` |
| `request_uuid` | random UUID version 4 strings | `"9bfe2c93-717e-4a45-b91b-55422c5af4ff"` |

The `request_json_*` versions use the same ids.

```pycon
>>> from jsonrpcclient import request, request_hex, request_random, request_uuid
>>> request("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
>>> request_hex("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': '1'}
>>> request_random("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': '...'}
>>> request_uuid("ping")
{'jsonrpc': '2.0', 'method': 'ping', 'id': '...-...-...-...-...'}
```

## The sequences are shared by the whole process

Each style has one sequence, created when jsonrpcclient is imported. Every
caller in the process shares it: two parts of your program that both call
`request` get ids 1 and 2, not 1 and 1. The sequences are safe to use from
several threads at once (see [Threads and async](threads.md)).

The ids restart from 1 in each new process. If several processes send
requests to the same server and the server cares about ids being unique, use
`request_uuid`.

## Choosing your own id

Pass `id` to any request function and the sequence is not used:

```pycon
>>> request("ping", id="job-42")
{'jsonrpc': '2.0', 'method': 'ping', 'id': 'job-42'}
```

`id=None` sends `"id": null`. It is not a notification: the server still
replies. Use [`notification`](notifications.md) when you want no reply.

## Your own sequence

`jsonrpcclient.id_generators` has the iterators behind the four styles. Each
call returns a new, independent iterator, so you can give a client or a
connection its own sequence. Take ids with `next()`:

```pycon
>>> from jsonrpcclient.id_generators import decimal, hexadecimal, random, uuid
>>> ids = decimal(start=100)
>>> request("ping", id=next(ids))
{'jsonrpc': '2.0', 'method': 'ping', 'id': 100}
>>> request("ping", id=next(ids))
{'jsonrpc': '2.0', 'method': 'ping', 'id': 101}
>>> next(hexadecimal(start=10))
'a'
>>> len(next(random(length=12)))
12
>>> len(next(uuid()))
36
```

These iterators are thread-safe. If you write your own, make sure it is too,
or keep it to one thread. `itertools.count()` isn't documented as
thread-safe, so prefer `id_generators.decimal()`.

## Which style to use

- `request`, for most programs. Small integers are easy to read in logs.
- `request_uuid`, when several processes or machines talk to one server, or
  when an id must never repeat.
- `request_random`, for short ids that don't reveal how many requests you
  sent. They are not guaranteed to be unique.
- `request_hex`, if your server expects hex strings.
