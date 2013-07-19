import traceback
import zmq
import json

from werp import nlog
from werp.common import sockets
from werp.uatrains.engine import drv

try:
    ctx = zmq.Context()
    froxly_data_server_socket = ctx.socket(zmq.REQ)
    froxly_data_server_socket.connect(sockets.froxly_data_server)
    froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
        {'url': drv.southwest.domain}}))
    froxly_data_server_socket.recv_unicode()
except:
    nlog.info('uatrains bot - etrain check proxies error', traceback.format_exc())