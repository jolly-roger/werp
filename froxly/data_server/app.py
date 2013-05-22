import datetime
import zmq
import traceback
import redis
import random
import json

from werp import orm
from werp import nlog
from werp.common import sockets
from werp.common import red_keys
from werp.froxly.data_server.checker import app as checker_app
from werp.froxly.data_server import common as data_server_common

conn = None
ses = None
try:
    ctx = zmq.Context()
    froxly_data_server_socket = ctx.socket(zmq.REP)
    froxly_data_server_socket.bind(sockets.froxly_data_server)
    froxly_checker_server_socket = ctx.socket(zmq.PUSH)
    froxly_checker_server_socket.connect(sockets.froxly_checker_server)
    red = redis.StrictRedis(unix_socket_path=sockets.redis)
    def rnd(msg):
        rnd_free_proxy = None
        if msg is not None and msg['params'] is not None and 'url' in msg['params'] and msg['params']['url'] is not None:
            url_red_key = red_keys.froxly_url_free_proxy_prefix + msg['params']['url']
            if red.exists(url_red_key) and red.scard(url_red_key) > 0:
                rnd_free_proxy = red.srandmember(url_red_key)
            else:
                nlog.info('froxly - rnd free proxy error', 'No proxies for url: ' + msg['params']['url'])
                rnd_free_proxy = rnd(None)
        else:
            if red.exists(red_keys.froxly_base_check_free_proxy) and \
                red.scard(red_keys.froxly_base_check_free_proxy) > 0:
                rnd_free_proxy = red.srandmember(red_keys.froxly_base_check_free_proxy)
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
                rnd_free_proxy = red.srandmember(red_keys.froxly_base_check_free_proxy)
        if rnd_free_proxy is not None:
            froxly_data_server_socket.send_unicode(json.dumps({'result': json.loads(rnd_free_proxy.decode('utf-8'))}))
        else:
            froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
            nlog.info('froxly - rnd free proxy error', 'Random free proxy is None')
    def activate(msg):
        pass
    def deactivate(msg):
        pass
    def check(msg):
        msg['method'] = 'base_check'
        
        nlog.info('froxly - data server info', json.dumps(msg))
        
        froxly_checker_server_socket.send_unicode(json.dumps(msg))
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def list_for_url(msg):
        msg['method'] = 'url_check'
        froxly_checker_server_socket.send_unicode(json.dumps(msg))
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def deactivate_for_url(msg):
        if 'proxy' in msg['params'] and 'url' in msg['params']:
            red.srem(red_keys.froxly_url_free_proxy_prefix + msg['params']['url'], msg['params']['proxy'])
            if 'reason' in msg['params']:
                red.sadd(red_keys.froxly_url_free_proxy_log_prefix + msg['params']['url'], msg['params']['reason'])
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def rnd_for_url(msg):
        rnd(msg)
    def clear_for_url(msg):
        if 'url' in msg['params']:
            red.delete(red_keys.froxly_url_free_proxy_prefix + msg['params']['url'])
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    methods = {}
    methods[rnd.__name__] = rnd
    methods[activate.__name__] = activate
    methods[deactivate.__name__] = deactivate
    methods[check.__name__] = check
    methods[list_for_url.__name__] = list_for_url
    methods[deactivate_for_url.__name__] = deactivate_for_url
    methods[rnd_for_url.__name__] = rnd_for_url
    methods[clear_for_url.__name__] = clear_for_url
    while True:
        try:
            msg = json.loads(froxly_data_server_socket.recv_unicode())
            if msg['method'] in methods:
                methods[msg['method']](msg)
        except:
            froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
            nlog.info('froxly - data server error', traceback.format_exc())
except:
    nlog.info('froxly - data server fatal', traceback.format_exc())
    if ses is not None:
        ses.close()
    if conn is not None:    
        conn.close()