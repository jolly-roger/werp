import datetime
import zmq
import traceback
import json
import threading

from werp import nlog
from werp.common import sockets
from werp.froxly.data_server import worker

WORKER_POOL = 32

try:
    ctx = zmq.Context()
    froxly_data_server_socket = ctx.socket(zmq.REP)
    froxly_data_server_socket.bind(sockets.froxly_data_server)
    froxly_checker_server_socket = ctx.socket(zmq.PUSH)
    froxly_checker_server_socket.connect(sockets.froxly_checker_server)
    froxly_data_worker_socket = ctx.socket(zmq.REQ)
    froxly_data_worker_socket.bind(sockets.froxly_data_worker)
    def check(msg):
        msg['method'] = 'base_check'
        froxly_checker_server_socket.send_unicode(json.dumps(msg))
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def list_for_url(msg):
        msg['method'] = 'url_check'
        froxly_checker_server_socket.send_unicode(json.dumps(msg))
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    for wrk_num in range(WORKER_POOL):
        thr = threading.Thread(target=worker.run)
        thr.start()
    methods = {}
    methods[check.__name__] = check
    methods[list_for_url.__name__] = list_for_url
    while True:
        try:
            msg = json.loads(froxly_data_server_socket.recv_unicode())
            if msg['method'] in methods:
                methods[msg['method']](msg)
            else:
                froxly_data_worker_socket.send_unicode(msg)
                res_msg = froxly_data_worker_socket.recv_unicode()
                froxly_data_server_socket.send_unicode(res_msg)
        except:
            froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
            nlog.info('froxly - data server error', traceback.format_exc())
except:
    nlog.info('froxly - data server fatal', traceback.format_exc())