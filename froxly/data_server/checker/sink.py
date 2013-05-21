import traceback
import zmq
import json
import redis

from werp import orm
from werp import nlog
from werp.common import sockets
from werp.common import red_keys
from werp.froxly.data_server import common as data_server_common

def run():
    conn = None
    ses = None
    try:
        red = redis.StrictRedis(unix_socket_path=sockets.redis)
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        ctx = zmq.Context()
        froxly_checker_res = ctx.socket(zmq.PULL)
        froxly_checker_res.bind(sockets.froxly_checker_res)
        froxly_checker_finish = ctx.socket(zmq.REP)
        froxly_checker_finish.bind(sockets.froxly_checker_finish)
        while True:
            proxy_count = int(froxly_checker_finish.recv_unicode())
            while True:
                task = json.loads(froxly_checker_res.recv_unicode())
                proxy = ses.query(orm.FreeProxy).filter(orm.FreeProxy.id == task['proxy']['id']).one()
                proxy.http_status = task['proxy']['http_status']
                proxy.http_status_reason = task['proxy']['http_status_reason']
                ses.commit()
                sproxy = data_server_common.jproxy2sproxy(task['proxy'])
                if task['proxy']['http_status'] == 200:
                    red.sadd(task['red_key'], sproxy)
                else:
                    if red.exists(task['red_key']) and red.sismember(task['red_key'], sproxy):
                        red.srem(task['red_key'], sproxy)
                proxy_count = proxy_count - 1
                
                nlog.info('froxly - checher sink info', str(proxy_count))
                
                if proxy_count == 0:
                    break
            froxly_checker_finish.send_unicode(str(0))
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
        if ses is not None:
            ses.close()
        if conn is not None:    
            conn.close()