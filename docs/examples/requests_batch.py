import logging

import requests

from jsonrpcclient import Error, Ok, parse, request

response = requests.post(
    "http://localhost:5000/", json=[request("ping") for _ in range(3)], timeout=10
)
for parsed in parse(response.json()):
    if isinstance(parsed, Ok):
        print(parsed.result)
    elif isinstance(parsed, Error):
        logging.error(parsed.message)
