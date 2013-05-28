import urllib.parse
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
    froxly_requester_server_socket = ctx.socket(zmq.REQ)
    froxly_requester_server_socket.bind(sockets.froxly_requester_server)
    def check(msg):
        msg['method'] = 'base_check'
        froxly_checker_server_socket.send_unicode(json.dumps(msg))
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def list_for_url(msg):
        msg['method'] = 'url_check'
        froxly_checker_server_socket.send_unicode(json.dumps(msg))
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def request(msg):
        url_obj = urllib.parse.urlparse(msg['params']['url'])
        proxy_req = {'method': 'rnd_for_url', 'params': None}
        if url_obj.netloc is not None and url_obj.netloc != '':
            proxy_req['params'] = {'url': url_obj.scheme + '://' + url_obj.netloc}
        froxly_data_worker_socket.send_unicode(json.dumps(proxy_req))
        proxy = json.loads(froxly_data_worker_socket.recv_unicode())['result']
        msg['params']['proxy'] = proxy
        froxly_requester_server_socket.send_unicode(json.dumps(msg))
        res_msg = froxly_requester_server_socket.recv_unicode()
        froxly_requester_server_socket.send_unicode(res_msg)
    for wrk_num in range(WORKER_POOL):
        thr = threading.Thread(target=worker.run)
        thr.start()
    checker_methods = {}
    checker_methods[check.__name__] = check
    checker_methods[list_for_url.__name__] = list_for_url
    requester_methods = {}
    requester_methods[request.__name__] = request
    while True:
        try:
            req_msg = froxly_data_server_socket.recv_unicode()
            msg = json.loads(req_msg)
            if msg['method'] in checker_methods:
                checker_methods[msg['method']](msg)
            elif msg['method'] in requester_methods:
                requester_methods[msg['method']](msg)
            else:
                froxly_data_worker_socket.send_unicode(req_msg)
                res_msg = froxly_data_worker_socket.recv_unicode()
                froxly_data_server_socket.send_unicode(res_msg)
        except:
            froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
            nlog.info('froxly - data server error', traceback.format_exc())
except:
    nlog.info('froxly - data server fatal', traceback.format_exc())