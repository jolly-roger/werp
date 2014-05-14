import traceback
import zmq
import json
import redis
import threading
import os.path
import random
import psycopg2

from werp import froxly_checker_log
from werp.common import sockets, red_keys
from werp.froxly.data_server.checker import sink, worker
from werp.froxly.data_server import common as data_server_common

def base_run(url):
    conn = None
    cur = None
    try:
        if not os.path.exists(sockets.get_socket_path(sockets.froxly_checker_worker, url)):
            ctx = zmq.Context()
            
            froxly_checker_worker_socket = ctx.socket(zmq.PUSH)
            froxly_checker_worker_socket.bind(sockets.format_socket_uri(sockets.froxly_checker_worker, url=url))
            
            conn = psycopg2.connect('host=localhost port=5432 dbname=werp user=werp password=0v}II587')
            cur = conn.cursor()
            cur.execute("select id, ip, port, protocol from free_proxy;")
            proxies = cur.fetchall()
            cur.close()
            conn.close()

            manager = threading.Thread(target=sink.run, args=(url, len(proxies)))
            manager.start()
            
            for wrk_num in range(data_server_common.CHECKER_BASE_WORKER_POOL):
                thr = threading.Thread(target=worker.run, args=(url,))
                thr.start()
            
            for proxy in proxies:
                task = {'url': url, 'red_key': red_keys.froxly_base_check_free_proxy,
                    'proxy': {'id': proxy[0], 'ip': proxy[1], 'port': proxy[2], 'protocol': proxy[3]}}
                froxly_checker_worker_socket.send_unicode(json.dumps(task))
               
            froxly_checker_finish_socket = ctx.socket(zmq.SUB)
            froxly_checker_finish_socket.connect(sockets.format_socket_uri(sockets.froxly_checker_finish, url=url))
            froxly_checker_finish_socket.setsockopt_string(zmq.SUBSCRIBE, '')
            froxly_checker_finish_socket.recv_unicode()
        else:
            froxly_checker_log.info('ventilator "base_run" is already started for url' + url)
    except:
        froxly_checker_log.exception('ventilator "base_run"\n\n' + traceback.format_exc())
        if cur is not None:    
            cur.close()
        if conn is not None:    
            conn.close()
def url_run(url, worker_pool=None, to_check_key=None):
    try:
        if not os.path.exists(sockets.get_socket_path(sockets.froxly_checker_worker, url)):
            ctx = zmq.Context()
            
            froxly_checker_worker_socket = ctx.socket(zmq.PUSH)
            froxly_checker_worker_socket.bind(sockets.format_socket_uri(sockets.froxly_checker_worker, url=url))
            
            red = redis.StrictRedis(unix_socket_path=sockets.redis)
            proxies = []
            
            if to_check_key is not None:
                proxies = red.smembers(to_check_key)
            else:
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
            froxly_checker_log.info('ventilator "url_run" is already started for url' + url)
    except:
        froxly_checker_log.exception('ventilator "url_run"\n\n' + traceback.format_exc())