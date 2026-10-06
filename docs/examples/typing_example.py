from typing import Any, Dict, List

from jsonrpcclient import Error, Ok, parse
from jsonrpcclient.responses import Response


def describe(response: Response) -> str:
    if isinstance(response, Ok):
        return f"result {response.result!r}"
    return f"error {response.code}: {response.message}"


def result_of(data: Dict[str, Any]) -> Any:
    parsed = parse(data)  # Ok | Error
    if isinstance(parsed, Error):
        raise RuntimeError(parsed.message)
    return parsed.result  # mypy knows parsed is an Ok here


batch: List[Dict[str, Any]] = [
    {"jsonrpc": "2.0", "result": "pong", "id": 1},
    {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": 2,
    },
]
for response in parse(batch):  # Iterator[Ok | Error]
    print(describe(response))
print(result_of({"jsonrpc": "2.0", "result": 5, "id": 3}))
