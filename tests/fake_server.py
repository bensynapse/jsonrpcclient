"""A small JSON-RPC 2.0 server for running the documentation examples.

It uses only the standard library. tests/doc_examples.py starts it for code
blocks marked <!-- server -->, and docs/examples/check_examples.py uses
respond() for every transport.

Methods:
    ping        returns "pong"
    add         returns the sum of the positional params
    anything else gives a -32601 "Method not found" error

Over HTTP it answers POST / only. Any other path gives a 404 HTML page, like a
misconfigured URL would. A request with only notifications gets 204 and no
body.
"""

import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Generator, List, Optional

PORT = 8000


def _error(code: int, message: str, id: Any = None) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": id}


def _handle(request: Any) -> Optional[Dict[str, Any]]:
    """Answer one request object, or return None for a notification."""
    if (
        not isinstance(request, dict)
        or request.get("jsonrpc") != "2.0"  # pyright: ignore[reportUnknownMemberType]
        or not isinstance(request.get("method"), str)  # pyright: ignore[reportUnknownMemberType]
    ):
        return _error(-32600, "Invalid Request")
    checked: Dict[str, Any] = request  # pyright: ignore[reportUnknownVariableType]
    method: str = checked["method"]
    params: Any = checked.get("params", [])
    if method == "ping":
        reply: Dict[str, Any] = {"jsonrpc": "2.0", "result": "pong"}
    elif method == "add" and isinstance(params, list):
        reply = {"jsonrpc": "2.0", "result": sum(params)}  # pyright: ignore[reportUnknownArgumentType]
    else:
        reply = _error(-32601, "Method not found")
    if "id" not in checked:
        return None
    reply["id"] = checked["id"]
    return reply


def respond(body: str, reject_batches: bool = False) -> Optional[str]:
    """Return the JSON reply to a request body, or None if there is no reply.

    With reject_batches, every batch gets the single error object that
    JSON-RPC 2.0 servers send for an invalid batch.
    """
    try:
        deserialized: Any = json.loads(body)
    except ValueError:
        return json.dumps(_error(-32700, "Parse error"))
    if isinstance(deserialized, list):
        if reject_batches or not deserialized:
            return json.dumps(_error(-32600, "Invalid Request"))
        replies: List[Dict[str, Any]] = []
        for request in deserialized:  # pyright: ignore[reportUnknownVariableType]
            reply = _handle(request)
            if reply is not None:
                replies.append(reply)
        return json.dumps(replies) if replies else None
    reply = _handle(deserialized)
    return None if reply is None else json.dumps(reply)


class _Handler(BaseHTTPRequestHandler):
    reject_batches = False

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if self.path != "/":
            page = b"<html><body><h1>404 Not Found</h1></body></html>"
            self.send_response(404)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
            return
        reply = respond(body.decode(), self.reject_batches)
        if reply is None:
            self.send_response(204)
            self.end_headers()
            return
        data = reply.encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: Any) -> None:
        pass


@contextmanager
def http_server(
    port: int = PORT, reject_batches: bool = False
) -> Generator[None, None, None]:
    """Run the server on localhost in a background thread."""
    handler = type("Handler", (_Handler,), {"reject_batches": reject_batches})
    server = ThreadingHTTPServer(("localhost", port), handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
