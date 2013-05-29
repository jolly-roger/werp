import urllib.parse
import datetime
import zmq
import traceback
import json
import threading

from werp import nlog
from werp.common import sockets
from werp.froxly.data_server import common as data_server_common
from werp.froxly.data_server import worker

WORKER_POOL = 32

try:
    ctx = zmq.Context()
    
    # data server frontend socket
    froxly_data_server_socket = ctx.socket(zmq.ROUTER)
    froxly_data_server_socket.bind(sockets.froxly_data_server)
    
    # data server worker backend socket
    froxly_data_worker_socket = ctx.socket(zmq.DEALER)
    froxly_data_worker_socket.bind(sockets.froxly_data_worker)
    
    # requester server backend socket
    froxly_requester_server_socket = ctx.socket(zmq.DEALER)
    froxly_requester_server_socket.bind(sockets.froxly_requester_server)
    
    # checker server backend socket
    froxly_checker_server_socket = ctx.socket(zmq.PUSH)
    froxly_checker_server_socket.connect(sockets.froxly_checker_server)
    
    poller = zmq.Poller()
    poller.register(froxly_data_server_socket, zmq.POLLIN)
    poller.register(froxly_data_worker_socket, zmq.POLLIN)
    poller.register(froxly_requester_server_socket, zmq.POLLIN)

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
        rnd_proxy_req = {'method': 'rnd_for_url', 'params': None}
        rnd_proxy_url = None
        if url_obj.netloc is not None and url_obj.netloc != '':
            rnd_proxy_url = url_obj.scheme + '://' + url_obj.netloc
            rnd_proxy_req['params'] = {'url': rnd_proxy_url}
        froxly_data_worker_socket.send_unicode(json.dumps(rnd_proxy_req))
        rnd_proxy = json.loads(froxly_data_worker_socket.recv_unicode())['result']
        msg['params']['proxy'] = rnd_proxy
        froxly_requester_server_socket.send_unicode(json.dumps(msg))
        worker_res_msg = froxly_requester_server_socket.recv_unicode()
        worker_res = json.loads(worker_res_msg)
        if rnd_proxy_url is not None and worker_res['result']['http_status'] is not None and \
            worker_res['result']['http_status'] == -11:
            sproxy = data_server_common.jproxy2sproxy(rnd_proxy)
            deactivate_proxy_req = {'method': 'deactivate_for_url', 'params':
                {'url': rnd_proxy_url, 'proxy': sproxy, 'reason': worker_res['result']['http_status_reason']}}
            froxly_data_worker_socket.send_unicode(json.dumps(deactivate_proxy_req))
            froxly_data_worker_socket.recv_unicode()
        froxly_data_server_socket.send_unicode(worker_res_msg)
        
    for wrk_num in range(WORKER_POOL):
        thr = threading.Thread(target=worker.run)
        thr.start()
    checker_methods = {}
    #checker_methods[check.__name__] = check
    #checker_methods[list_for_url.__name__] = list_for_url
    requester_methods = {}
    #requester_methods[request.__name__] = request
    
    while True:
        sockets = dict(poller.poll())
        try:
            # data server frontend
            if froxly_data_server_socket in sockets and  sockets[froxly_data_server_socket] == zmq.POLLIN:
                req_msg = froxly_data_server_socket.recv_multipart()
                msg = json.loads(req_msg[2].decode())
                if msg['method'] in checker_methods:
                    checker_methods[msg['method']](msg)
                elif msg['method'] in requester_methods:
                    requester_methods[msg['method']](msg)
                else:
                    froxly_data_worker_socket.send_multipart(req_msg)
            
            # data server worker backend
            if froxly_data_worker_socket in sockets and  sockets[froxly_data_worker_socket] == zmq.POLLIN:
                res_msg = froxly_data_worker_socket.recv_multipart()
                froxly_data_server_socket.send_multipart(res_msg)
            
            # requester server backend
            if froxly_requester_server_socket in sockets and  sockets[froxly_requester_server_socket] == zmq.POLLIN:
                res_msg = froxly_requester_server_socket.recv_multipart()
                froxly_data_server_socket.send_multipart(res_msg) 
        except:
            #froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
            nlog.info('froxly - data server error', traceback.format_exc())
except:
    nlog.info('froxly - data server fatal', traceback.format_exc())