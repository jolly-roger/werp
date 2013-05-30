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
    
    # data server frontend socket
    froxly_data_server_socket = ctx.socket(zmq.ROUTER)
    froxly_data_server_socket.bind(sockets.froxly_data_server)
    
    # data server worker backend socket
    froxly_data_worker_socket = ctx.socket(zmq.DEALER)
    froxly_data_worker_socket.bind(sockets.froxly_data_worker)
    
    # requester server backend socket
    froxly_requester_server_socket = ctx.socket(zmq.DEALER)
    froxly_requester_server_socket.connect(sockets.froxly_requester_server)
    
    # checker server backend socket
    froxly_checker_server_socket = ctx.socket(zmq.PUSH)
    froxly_checker_server_socket.connect(sockets.froxly_checker_server)
    
    poller = zmq.Poller()
    poller.register(froxly_data_server_socket, zmq.POLLIN)
    poller.register(froxly_data_worker_socket, zmq.POLLIN)
    poller.register(froxly_requester_server_socket, zmq.POLLIN)

    def check(msg, req_msg):
        msg['method'] = 'base_check'
        froxly_checker_server_socket.send_unicode(json.dumps(msg))
        req_msg[2] = json.dumps({'result': None}).encode()
        froxly_data_server_socket.send_multipart(req_msg)
    def list_for_url(msg, req_msg):
        msg['method'] = 'url_check'
        froxly_checker_server_socket.send_unicode(json.dumps(msg))
        req_msg[2] = json.dumps({'result': None}).encode()
        froxly_data_server_socket.send_multipart(req_msg)
        
    for wrk_num in range(WORKER_POOL):
        thr = threading.Thread(target=worker.run)
        thr.start()
    checker_methods = {}
    checker_methods[check.__name__] = check
    checker_methods[list_for_url.__name__] = list_for_url
    
    while True:
        socks = dict(poller.poll())
        try:
            # data server frontend
            if froxly_data_server_socket in socks and socks[froxly_data_server_socket] == zmq.POLLIN:
                req_msg = froxly_data_server_socket.recv_multipart()
                msg = json.loads(req_msg[2].decode())
                if msg['method'] in checker_methods:
                    checker_methods[msg['method']](msg, req_msg)
                elif msg['method'] == 'request':
                    
                    nlog.info('froxly - data server info', str(req_msg))
                    
                    froxly_requester_server_socket.send_multipart(req_msg)
                else:
                    froxly_data_worker_socket.send_multipart(req_msg)
            
            # data server worker backend
            if froxly_data_worker_socket in socks and  socks[froxly_data_worker_socket] == zmq.POLLIN:
                res_msg = froxly_data_worker_socket.recv_multipart()
                froxly_data_server_socket.send_multipart(res_msg)
            
            # requester server backend
            if froxly_requester_server_socket in socks and socks[froxly_requester_server_socket] == zmq.POLLIN:
                res_msg = froxly_requester_server_socket.recv_multipart()
                froxly_data_server_socket.send_multipart(res_msg) 
        except:
            #froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
            nlog.info('froxly - data server error', traceback.format_exc())
except:
    nlog.info('froxly - data server fatal', traceback.format_exc())