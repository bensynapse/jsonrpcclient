import requests

from jsonrpcclient import Error, Ok, parse, request

url = "http://localhost:8000/"
response = requests.post(url, json=request("ping"), timeout=10)
response.raise_for_status()
parsed = parse(response.json())
if isinstance(parsed, Ok):
    print(parsed.result)
elif isinstance(parsed, Error):
    print("Error:", parsed.message)
