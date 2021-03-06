import urllib.request
import urllib.parse
import traceback
import datetime
import zmq
import json
import socket
import redis

from werp import orm
from werp import nlog
from werp.common import sockets
from werp.common import timeouts
from werp.common import red_keys
from werp.froxly.data_server import common as data_server_common

def run():
    try:
        ctx = zmq.Context()
        froxly_data_worker_socket = ctx.socket(zmq.REP)
        froxly_data_worker_socket.connect(sockets.froxly_data_worker)
        red = redis.StrictRedis(unix_socket_path=sockets.redis)
        def rnd(msg):
            rnd_free_proxy = None
            def base_rnd():
                if red.exists(red_keys.froxly_base_check_free_proxy) and \
                    red.scard(red_keys.froxly_base_check_free_proxy) > 0:
                    return red.srandmember(red_keys.froxly_base_check_free_proxy)
                else:
                    conn = orm.null_engine.connect()
                    ses = orm.sescls(bind=conn)
                    free_proxies = ses.query(orm.FreeProxy).filter(orm.and_(orm.FreeProxy.protocol == 'http',
                        orm.FreeProxy.http_status == 200)).all()
                    for free_proxy in free_proxies:
                        sproxy = data_server_common.dbproxy2sproxy(free_proxy)
                        red.sadd(red_keys.froxly_base_check_free_proxy, sproxy)
                    ses.close()
                    conn.close()
                    return red.srandmember(red_keys.froxly_base_check_free_proxy)
            if msg is not None and msg['params'] is not None and 'url' in msg['params'] and \
                msg['params']['url'] is not None:
                url_red_key = red_keys.froxly_url_free_proxy_prefix + msg['params']['url']
                if red.exists(url_red_key) and red.scard(url_red_key) > 0:
                    rnd_free_proxy = red.srandmember(url_red_key)
                else:
                    red.rpush(red_keys.froxly_rnd_free_proxy_log, 'No proxies for url: ' + msg['params']['url'])
                    rnd_free_proxy = base_rnd()
            else:
                rnd_free_proxy = base_rnd()
            if rnd_free_proxy is not None:
                froxly_data_worker_socket.send_unicode(json.dumps({'result': json.loads(rnd_free_proxy.decode('utf-8'))}))
            else:
                froxly_data_worker_socket.send_unicode(json.dumps({'result': None}))
                nlog.info('froxly - rnd free proxy error', 'Random free proxy is None')
        def activate(msg):
            pass
        def deactivate(msg):
            pass
        def deactivate_for_url(msg):
            if 'proxy' in msg['params'] and 'url' in msg['params']:
                red.srem(red_keys.froxly_url_free_proxy_prefix + msg['params']['url'], msg['params']['proxy'])
                if 'reason' in msg['params']:
                    red.sadd(red_keys.froxly_url_free_proxy_log_prefix + msg['params']['url'],
                        '[' + str(datetime.datetime.now()) + '] ' + msg['params']['reason'])
            froxly_data_worker_socket.send_unicode(json.dumps({'result': None}))
        def rnd_for_url(msg):
            rnd(msg)
        def clear_for_url(msg):
            if 'url' in msg['params']:
                red.delete(red_keys.froxly_url_free_proxy_prefix + msg['params']['url'])
            froxly_data_worker_socket.send_unicode(json.dumps({'result': None}))
        methods = {}
        methods[rnd.__name__] = rnd
        methods[activate.__name__] = activate
        methods[deactivate.__name__] = deactivate
        methods[deactivate_for_url.__name__] = deactivate_for_url
        methods[rnd_for_url.__name__] = rnd_for_url
        methods[clear_for_url.__name__] = clear_for_url
        while True:
            try:
                msg = json.loads(froxly_data_worker_socket.recv_unicode())
                if msg['method'] in methods:
                    methods[msg['method']](msg)
            except:
                froxly_data_worker_socket.send_unicode(json.dumps({'result': None}))
                nlog.info('froxly - data server error', traceback.format_exc())
    except:
        nlog.info('froxly - data worker fatal', traceback.format_exc())