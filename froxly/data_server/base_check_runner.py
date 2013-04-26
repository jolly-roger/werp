import json
import zmq
import time
import datetime

from werp import nlog
from werp.common import sockets

ctx = None
try:
    start_time = time.time()
    ctx = zmq.Context()
    froxly_data_server_socket = ctx.socket(zmq.REQ)
    froxly_data_server_socket.connect(sockets.froxly_data_server)
    froxly_data_server_socket.send_unicode(json.dumps({'method': 'check', 'params': None}))
    froxly_data_server_socket.recv_unicode()
    ctx.destroy()
    end_time = time.time()
    exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
    nlog.info('froxly - base check', str(exec_delta))
except:
    nlog.info('froxly - base check fatal', traceback.format_exc())
    if ctx is not None:
        ctx.destroy()