import logging

import requests

from jsonrpcclient import Error, Ok, parse, request

batch = [request("ping") for _ in range(3)]
response = requests.post("http://localhost:8000/", json=batch, timeout=10)
response.raise_for_status()
data = response.json()
if isinstance(data, dict):
    # The server rejected the whole batch. It sends one error object, not a list.
    logging.error("Batch rejected: %s", parse(data))
else:
    for parsed in parse(data):
        if isinstance(parsed, Ok):
            print(parsed.result)
        elif isinstance(parsed, Error):
            logging.error(parsed.message)
