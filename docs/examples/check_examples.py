"""Run each example in this directory against a small local test server.

Usage: python docs/examples/check_examples.py

Each example must exit cleanly and print "pong" once per request. The server
listens on port 5000, like the examples expect. Needs the packages in
requirements/examples.txt.
"""

import asyncio
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Iterator, List

import zmq
from websockets.asyncio.server import ServerConnection, serve

HERE = Path(__file__).parent
PORT = 5000


def respond(body: str) -> str:
    """Answer every request with "pong", as the examples expect."""
    deserialized = json.loads(body)
    requests = deserialized if isinstance(deserialized, list) else [deserialized]
    responses = [{"jsonrpc": "2.0", "result": "pong", "id": r["id"]} for r in requests]
    return json.dumps(responses if isinstance(deserialized, list) else responses[0])


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers["Content-Length"])).decode()
        reply = respond(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)

    def log_message(self, format: str, *args: Any) -> None:
        pass


def http_server() -> Iterator[None]:
    server = ThreadingHTTPServer(("localhost", PORT), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    yield
    server.shutdown()
    server.server_close()
    thread.join()


def websockets_server() -> Iterator[None]:
    loop = asyncio.new_event_loop()
    started = threading.Event()
    stop: asyncio.Future[None] = loop.create_future()

    async def handler(websocket: ServerConnection) -> None:
        async for message in websocket:
            await websocket.send(respond(str(message)))

    async def main() -> None:
        async with serve(handler, "localhost", PORT):
            started.set()
            await stop

    thread = threading.Thread(target=loop.run_until_complete, args=(main(),))
    thread.start()
    started.wait(10)
    yield
    loop.call_soon_threadsafe(stop.set_result, None)
    thread.join()
    loop.close()


def zeromq_server() -> Iterator[None]:
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")

    def serve_one() -> None:
        socket.send_string(respond(socket.recv().decode()))

    thread = threading.Thread(target=serve_one)
    thread.start()
    yield
    thread.join(10)
    socket.close()
    context.term()


CASES: List[tuple] = [
    (http_server, "requests_client.py", 1),
    (http_server, "requests_batch.py", 3),
    (http_server, "aiohttp_client.py", 1),
    (websockets_server, "websockets_client.py", 1),
    (zeromq_server, "zeromq_client.py", 1),
]


def run(server: Callable[[], Iterator[None]], example: str, pongs: int) -> bool:
    running = server()
    next(running)
    try:
        result = subprocess.run(
            [sys.executable, str(HERE / example)],
            capture_output=True,
            text=True,
            timeout=60,
        )
    finally:
        next(running, None)
    ok = result.returncode == 0 and result.stdout.split() == ["pong"] * pongs
    print(f"{'ok  ' if ok else 'FAIL'} {example}")
    if not ok:
        print(result.stdout, result.stderr, sep="\n")
    return ok


if __name__ == "__main__":
    results = [run(*case) for case in CASES]
    sys.exit(0 if all(results) else 1)
