import traceback
import threading
import zmq

from werp import nlog
from werp.common import sockets
from werp.ugently.data_server import worker

WORKER_POOL = 64

try:
    ctx = zmq.Context()
    
    ugently_data_server_socket = ctx.socket(zmq.ROUTER)
    ugently_data_server_socket.bind(sockets.ugently_data_server)
    
    ugently_data_worker_socket = ctx.socket(zmq.DEALER)
    ugently_data_worker_socket.bind(sockets.ugently_data_worker)
    
    poller = zmq.Poller()
    poller.register(ugently_data_server_socket, zmq.POLLIN)
    poller.register(ugently_data_worker_socket, zmq.POLLIN)
    
    for wrk_num in range(WORKER_POOL):
        thr = threading.Thread(target=worker.run)
        thr.start()
    
    while True:
        socks = dict(poller.poll())
        try:
            # frontend
            if ugently_data_server_socket in socks and socks[ugently_data_server_socket] == zmq.POLLIN:
                req_msg = ugently_data_server_socket.recv_multipart()
                ugently_data_worker_socket.send_multipart(req_msg)
            
            # backend
            if ugently_data_worker_socket in socks and socks[ugently_data_worker_socket] == zmq.POLLIN:
                res_msg = ugently_data_worker_socket.recv_multipart()
                ugently_data_server_socket.send_multipart(res_msg) 
        except:
            nlog.info('ugently - data server error', traceback.format_exc())
except:
    nlog.info('ugently - data server fatal', traceback.format_exc())