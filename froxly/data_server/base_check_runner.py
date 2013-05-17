import json
import zmq
import time
import datetime
import redis
import traceback

from werp import nlog
from werp.common import sockets
from werp.common import red_keys

ctx = None

try:
    start_dt = datetime.datetime.now()
    start_time = time.time()
    ctx = zmq.Context()
    froxly_data_server_socket = ctx.socket(zmq.REQ)
    froxly_data_server_socket.connect(sockets.froxly_data_server)
    froxly_data_server_socket.send_unicode(json.dumps({'method': 'check', 'params': None}))
    froxly_data_server_socket.recv_unicode()
    ctx.term()
    end_time = time.time()
    exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
    red = redis.StrictRedis(unix_socket_path=sockets.redis)
    red.rpush(red_keys.exec_time_log, 'froxly base check %s %s' % (str(start_dt), str(exec_delta)))
except:
    nlog.info('froxly - base check fatal', traceback.format_exc())
    if ctx is not None:
        ctx.term()