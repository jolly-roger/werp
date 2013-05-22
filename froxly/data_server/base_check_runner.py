import json
import zmq
import traceback

from werp import nlog
from werp.common import sockets

ctx = None

try:
    ctx = zmq.Context()
    froxly_data_server_socket = ctx.socket(zmq.REQ)
    froxly_data_server_socket.connect(sockets.froxly_data_server)
    froxly_data_server_socket.send_unicode(json.dumps({'method': 'check', 'params': None}))
    froxly_data_server_socket.recv_unicode()
except:
    nlog.info('froxly - base check fatal', traceback.format_exc())