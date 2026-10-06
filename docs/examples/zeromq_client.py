import logging

import zmq

from jsonrpcclient import Error, Ok, parse_json, request_json

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:8000")
socket.send_string(request_json("ping"))
parsed = parse_json(socket.recv())
socket.close()
context.term()
if isinstance(parsed, Ok):
    print(parsed.result)
elif isinstance(parsed, Error):
    logging.error(parsed.message)
