import traceback
import zmq
import json
import redis
import threading
import os.path

from werp import orm, nlog
from werp.common import sockets, red_keys
from werp.froxly.data_server.checker import sink, worker
from werp.froxly.data_server import common as data_server_common

def base_run(url):
    conn = None
    ses = None
    try:
        if not os.path.exists(sockets.get_socket_path(sockets.froxly_checker_worker, url)):
            ctx = zmq.Context()
            
            froxly_checker_worker_socket = ctx.socket(zmq.PUSH)
            froxly_checker_worker_socket.bind(sockets.format_socket_uri(sockets.froxly_checker_worker, url=url))
            
            conn = orm.null_engine.connect()
            ses = orm.sescls(bind=conn)
            proxies = ses.query(orm.FreeProxy).all()
            
            manager = threading.Thread(target=sink.run, args=(url, len(proxies)))
            manager.start()
            
            for wrk_num in range(data_server_common.CHECKER_BASE_WORKER_POOL):
                thr = threading.Thread(target=worker.run, args=(url,))
                thr.start()
            
            for proxy in proxies:
                task = {'url': url, 'red_key': red_keys.froxly_base_check_free_proxy,
                    'proxy': {'id': proxy.id, 'ip': proxy.ip, 'port': proxy.port, 'protocol': proxy.protocol}}
                froxly_checker_worker_socket.send_unicode(json.dumps(task))
               
            froxly_checker_finish_socket = ctx.socket(zmq.SUB)
            froxly_checker_finish_socket.connect(sockets.format_socket_uri(sockets.froxly_checker_finish, url=url))
            froxly_checker_finish_socket.setsockopt_string(zmq.SUBSCRIBE, '')
            froxly_checker_finish_socket.recv_unicode()
            ses.close()
            conn.close()
        else:
            nlog.info('froxly - checher info', 'Check for ' + url + ' already started')
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
        if ses is not None:
            ses.close()
        if conn is not None:    
            conn.close()
def url_run(url, worker_pool=None):
    try:
        if not os.path.exists(sockets.get_socket_path(sockets.froxly_checker_worker, url)):
            ctx = zmq.Context()
    
            froxly_checker_worker_socket = ctx.socket(zmq.PUSH)
            froxly_checker_worker_socket.bind(sockets.format_socket_uri(sockets.froxly_checker_worker, url=url))
            
            red = redis.StrictRedis(unix_socket_path=sockets.redis)
            proxies = red.smembers(red_keys.froxly_base_check_free_proxy)
            
            manager = threading.Thread(target=sink.run, args=(url, len(proxies)))
            manager.start()
            
            if worker_pool is None:
                worker_pool = data_server_common.CHECKER_WORKER_POOL
            
            for wrk_num in range(worker_pool):
                thr = threading.Thread(target=worker.run, args=(url,))
                thr.start()
            
            for p in proxies:
                proxy = json.loads(p.decode('utf-8'))
                task = {'url': url, 'red_key': red_keys.froxly_url_free_proxy_prefix + url,
                    'proxy': {'id': proxy['id'], 'ip': proxy['ip'], 'port': proxy['port'], 'protocol': proxy['protocol']}}
                froxly_checker_worker_socket.send_unicode(json.dumps(task))
            
            froxly_checker_finish_socket = ctx.socket(zmq.SUB)
            froxly_checker_finish_socket.connect(sockets.format_socket_uri(sockets.froxly_checker_finish, url=url))
            froxly_checker_finish_socket.setsockopt_string(zmq.SUBSCRIBE, '')
            froxly_checker_finish_socket.recv_unicode()
        else:
            nlog.info('froxly - checher info', 'Check for ' + url + ' already started')
    except:
        nlog.info('froxly - checher error', traceback.format_exc())