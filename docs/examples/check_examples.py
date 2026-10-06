"""Run each example in this directory against a small local test server.

Usage: python docs/examples/check_examples.py

Each example must exit cleanly and print what CASES expects. The servers
listen on port 8000, like the examples expect, and answer with
tests/fake_server.py. Needs the packages in requirements/examples.txt.
"""

import asyncio
import subprocess
import sys
import threading
from contextlib import contextmanager, nullcontext
from pathlib import Path
from typing import Callable, ContextManager, Iterator, List, NamedTuple

import zmq
from websockets.asyncio.server import ServerConnection, serve

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent))
from tests.fake_server import PORT, http_server, respond  # noqa: E402


@contextmanager
def batch_rejecting_http_server() -> Iterator[None]:
    with http_server(reject_batches=True):
        yield


@contextmanager
def websockets_server() -> Iterator[None]:
    loop = asyncio.new_event_loop()
    started = threading.Event()
    stop: asyncio.Future[None] = loop.create_future()

    async def handler(websocket: ServerConnection) -> None:
        async for message in websocket:
            reply = respond(str(message))
            if reply is not None:
                await websocket.send(reply)

    async def main() -> None:
        async with serve(handler, "localhost", PORT):
            started.set()
            await stop

    thread = threading.Thread(target=loop.run_until_complete, args=(main(),))
    thread.start()
    started.wait(10)
    try:
        yield
    finally:
        loop.call_soon_threadsafe(stop.set_result, None)
        thread.join()
        loop.close()


@contextmanager
def zeromq_server() -> Iterator[None]:
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")

    def serve_one() -> None:
        socket.send_string(respond(socket.recv().decode()) or "")

    thread = threading.Thread(target=serve_one)
    thread.start()
    try:
        yield
    finally:
        thread.join(10)
        socket.close()
        context.term()


class Case(NamedTuple):
    server: Callable[[], ContextManager[None]]
    example: str
    stdout: List[str]
    stderr: str = ""  # must appear in stderr


PONG = ["pong"]
CASES = [
    Case(http_server, "quickstart.py", PONG),
    Case(http_server, "urllib_client.py", PONG),
    Case(http_server, "requests_client.py", PONG),
    Case(http_server, "requests_batch.py", PONG * 3),
    # A server that rejects the whole batch replies with one error object.
    Case(
        batch_rejecting_http_server,
        "requests_batch.py",
        [],
        "Batch rejected: Error(code=-32600, message='Invalid Request', "
        "data=None, id=None)",
    ),
    Case(http_server, "httpx_client.py", PONG),
    Case(http_server, "httpx_async.py", PONG),
    Case(http_server, "aiohttp_client.py", PONG),
    Case(websockets_server, "websockets_client.py", PONG),
    Case(zeromq_server, "zeromq_client.py", PONG),
    Case(
        nullcontext,
        "typing_example.py",
        ["result", "'pong'", "error", "-32601:", "Method", "not", "found", "5"],
    ),
]


def run(case: Case) -> bool:
    with case.server():
        result = subprocess.run(
            [sys.executable, str(HERE / case.example)],
            capture_output=True,
            text=True,
            timeout=60,
        )
    ok = (
        result.returncode == 0
        and result.stdout.split() == case.stdout
        and case.stderr in result.stderr
    )
    server = getattr(case.server, "__name__", "no server")
    label = f"{case.example} ({server})"
    print(f"{'ok  ' if ok else 'FAIL'} {label}")
    if not ok:
        print(result.stdout, result.stderr, sep="\n")
    return ok


if __name__ == "__main__":
    results = [run(case) for case in CASES]
    sys.exit(0 if all(results) else 1)
