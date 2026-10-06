import logging

import zmq

from jsonrpcclient import Error, Ok, parse_json, request_json

socket = zmq.Context().socket(zmq.REQ)
socket.connect("tcp://localhost:5000")
socket.send_string(request_json("ping"))
parsed = parse_json(socket.recv())
if isinstance(parsed, Ok):
    print(parsed.result)
elif isinstance(parsed, Error):
    logging.error(parsed.message)
