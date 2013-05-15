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

from . import checker
from . import common as data_server_common

expire_delta = datetime.timedelta(days=1)
conn = None
ses = None
ctx = None
try:
    ctx = zmq.Context()
    froxly_data_server_socket = ctx.socket(zmq.REP)
    froxly_data_server_socket.bind(sockets.froxly_data_server)
    red = redis.StrictRedis(unix_socket_path=sockets.redis)
    def rnd(msg):
        rnd_free_proxy = None
        if msg is not None and msg['params'] is not None and 'url' in msg['params']:
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
        checker.base_check()
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def list_for_domain(msg):
        nlog.info('froxly - data server info', msg['params']['domain'])
        checker.url_check(msg['params']['domain'])
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def rnd_for_domain(msg):
        pass
    methods = {}
    methods[rnd.__name__] = rnd
    methods[activate.__name__] = activate
    methods[deactivate.__name__] = deactivate
    methods[check.__name__] = check
    methods[list_for_domain.__name__] = list_for_domain
    methods[rnd_for_domain.__name__] = rnd_for_domain
    checker.init()
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
    if ctx is not None:
        ctx.destroy()
    if ses is not None:
        ses.close()
    if conn is not None:    
        conn.close()