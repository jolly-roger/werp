import traceback
import threading
import zmq
import json

from werp import nlog
from werp.common import sockets

worker_pool = 32

try:
    ctx = zmq.Context()
    froxly_requester_server_socket = ctx.socket(zmq.REP)
    froxly_requester_server_socket.bind(sockets.froxly_requester_server)
    froxly_requester_worker_socket = ctx.socket(zmq.REQ)
    froxly_requester_worker_socket.bind(sockets.froxly_requester_worker)
    for wrk_num in range(worker_pool):
        thr = threading.Thread(target=worker.run)
        thr.start()
except:
    nlog.info('froxly - requester fatal', traceback.format_exc())