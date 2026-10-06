import logging
from urllib.request import Request, urlopen

from jsonrpcclient import Error, Ok, parse_json, request_json

http_request = Request(
    "http://localhost:8000/",
    data=request_json("ping").encode(),
    headers={"Content-Type": "application/json"},
)
# urlopen raises urllib.error.HTTPError for a 4xx or 5xx status.
with urlopen(http_request, timeout=10) as http_response:
    parsed = parse_json(http_response.read())
if isinstance(parsed, Ok):
    print(parsed.result)
elif isinstance(parsed, Error):
    logging.error(parsed.message)
