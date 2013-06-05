import traceback
import zmq
import json
import redis
import threading

from werp import orm
from werp import nlog
from werp.common import sockets
from werp.common import red_keys
from werp.froxly.data_server import common as data_server_common

def base_run(url):
    conn = None
    ses = None
    ctx = None
    try:
        ctx = zmq.Context()
        froxly_checker_req = ctx.socket(zmq.PUSH)
        froxly_checker_req.bind(sockets.froxly_checker_req)
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        proxies = ses.query(orm.FreeProxy).all()
        for proxy in proxies:
            task = {'url': url, 'red_key': red_keys.froxly_base_check_free_proxy,
                'proxy': {'id': proxy.id, 'ip': proxy.ip, 'port': proxy.port, 'protocol': proxy.protocol}}
            froxly_checker_req.send_unicode(json.dumps(task))
        froxly_checker_finish = ctx.socket(zmq.REQ)
        froxly_checker_finish.connect(sockets.froxly_checker_finish)
        froxly_checker_finish.send_unicode(str(len(proxies)))
        froxly_checker_finish.recv_unicode()
        ses.close()
        conn.close()
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
        if ses is not None:
            ses.close()
        if conn is not None:    
            conn.close()
def url_run(url):
    ctx = None
    try:
        ctx = zmq.Context()
        #socket_address = sockets.froxly_checker_req + '_' + 
        froxly_checker_req = ctx.socket(zmq.PUSH)
        froxly_checker_req.bind(sockets.froxly_checker_req)
        
        #for wrk_num in range(data_server_common.CHECKER_WORKER_POOL):
        #    thr = threading.Thread(target=worker.run, args=(None,))
        #    thr.start()
        
        red = redis.StrictRedis(unix_socket_path=sockets.redis)
        proxies = red.smembers(red_keys.froxly_base_check_free_proxy)
        for p in proxies:
            proxy = json.loads(p.decode('utf-8'))
            task = {'url': url, 'red_key': red_keys.froxly_url_free_proxy_prefix + url,
                'proxy': {'id': proxy['id'], 'ip': proxy['ip'], 'port': proxy['port'], 'protocol': proxy['protocol']}}
            froxly_checker_req.send_unicode(json.dumps(task))
        froxly_checker_finish = ctx.socket(zmq.REQ)
        froxly_checker_finish.connect(sockets.froxly_checker_finish)
        froxly_checker_finish.send_unicode(str(len(proxies)))
        froxly_checker_finish.recv_unicode()
    except:
        nlog.info('froxly - checher error', traceback.format_exc())