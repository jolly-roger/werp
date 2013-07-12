import json
import zmq
import traceback

from werp import nlog
from werp.common import sockets

conn = None
ses = None

try:
    ctx = zmq.Context()
    uatrains_bot_server_socket = ctx.socket(zmq.REQ)
    uatrains_bot_server_socket.connect(sockets.uatrains_bot_server)
    uatrains_bot_server_socket.send_unicode(json.dumps({'method': 'grab_etrain', 'params': None}))
    uatrains_bot_server_socket.recv_unicode()
except:
    nlog.info('uatrains bot - task runner fatal', traceback.format_exc())