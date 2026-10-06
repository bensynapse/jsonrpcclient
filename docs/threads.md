---
description: jsonrpcclient is thread-safe, works on free-threaded Python 3.14t, and fits asyncio because it does no I/O.
---

# Threads and async

## Threads

Every function in jsonrpcclient can be called from several threads at once.
That includes free-threaded Python (3.14t), where there is no GIL. The test
suite runs on 3.14t. It calls the request functions from many threads at
once and checks that no call fails and no id is handed out twice.

The request functions share one id sequence per style across the whole
process (see [Ids](ids.md)). Two threads calling `request` at the same time
always get different ids. The iterators in `jsonrpcclient.id_generators` are
thread-safe too, so you can share one between threads.

`parse` and `parse_json` keep no state. The only thing to watch is the lazy
iterator that `parse` returns for a batch: don't consume one iterator from
two threads. Call `list()` on it first if you need to share the responses.

!!! info "New in 4.0.4"
    Before 4.0.4, `request_hex`, `request_random` and `request_uuid` could
    raise `ValueError: generator already executing` when called from several
    threads at once, and free-threaded Python could crash.

## asyncio

jsonrpcclient does no I/O and never blocks, so you can call it directly in
async code. Use an async transport for the sending part: httpx's
`AsyncClient`, aiohttp or websockets. See [Transports](examples.md).

Requests made concurrently with `asyncio.gather` still get distinct ids. Their
responses can arrive in any order, so match them by id as you would for a
[batch](batches.md).
