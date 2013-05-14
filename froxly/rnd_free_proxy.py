import datetime
import zmq
import traceback
import redis
import random
import json

from werp import orm
from werp import nlog
from werp.common import sockets

ctx = None
try:
    start_dt = datetime.datetime.now()
    start_time = time.time()
    ctx = zmq.Context()
    froxly_data_server_socket = ctx.socket(zmq.REQ)
    froxly_data_server_socket.connect(sockets.froxly_data_server)
    rnd_free_proxy_socket = ctx.socket(zmq.REP)
    rnd_free_proxy_socket.bind(sockets.rnd_free_proxy)
    while True:
        msg = rnd_free_proxy_socket.recv_unicode()
        froxly_data_server_socket.send_unicode(json.dumps({'method': 'rnd', 'params': None}))
        rnd_free_proxy = json.loads(froxly_data_server_socket.recv_unicode())
        if rnd_free_proxy is not None:        
            rnd_free_proxy_socket.send_unicode(json.loads(rnd_free_proxy.decode('utf-8'))['result'])
        else:
            rnd_free_proxy_socket.send_unicode()
            nlog.info('froxly - rnd free proxy error', 'Random free proxy is None')
except:
    nlog.info('froxly - rnd free proxy error', traceback.format_exc())
    if ctx is not None:
        ctx.destroy()    