import traceback
import threading
import zmq

from werp import nlog
from werp.common import sockets
from werp.froxly.data_server.requester import worker

WORKER_POOL = 32

try:
    ctx = zmq.Context()
    
    froxly_requester_server_socket = ctx.socket(zmq.ROUTER)
    froxly_requester_server_socket.bind(sockets.froxly_requester_server)
    
    froxly_requester_worker_socket = ctx.socket(zmq.DEALER)
    froxly_requester_worker_socket.bind(sockets.froxly_requester_worker)
    
    poller = zmq.Poller()
    poller.register(froxly_requester_server_socket, zmq.POLLIN)
    poller.register(froxly_requester_worker_socket, zmq.POLLIN)
    
    for wrk_num in range(WORKER_POOL):
        thr = threading.Thread(target=worker.run)
        thr.start()
    
    while True:
        socks = dict(poller.poll())
        try:
            # frontend
            if froxly_requester_server_socket in socks and socks[froxly_requester_server_socket] == zmq.POLLIN:
                req_msg = froxly_requester_server_socket.recv_multipart()
                froxly_requester_worker_socket.send_multipart(req_msg)
            
            # backend
            if froxly_requester_worker_socket in socks and socks[froxly_requester_worker_socket] == zmq.POLLIN:
                res_msg = froxly_requester_worker_socket.recv_multipart()
                froxly_requester_server_socket.send_multipart(res_msg) 
        except:
            #froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
            nlog.info('froxly - data server error', traceback.format_exc())
except:
    nlog.info('froxly - requester server fatal', traceback.format_exc())