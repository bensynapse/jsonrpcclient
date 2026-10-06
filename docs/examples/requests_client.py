import logging

import requests

from jsonrpcclient import Error, Ok, parse, request

response = requests.post("http://localhost:8000/", json=request("ping"), timeout=10)
response.raise_for_status()
parsed = parse(response.json())
if isinstance(parsed, Ok):
    print(parsed.result)
elif isinstance(parsed, Error):
    logging.error(parsed.message)
