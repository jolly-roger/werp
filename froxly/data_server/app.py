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
from werp.froxly.data_server import checker

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
        froxly_free_proxy_keys = red.keys(red_keys.froxly_free_proxy + '*')
        rnd_free_proxy = None
        if len(froxly_free_proxy_keys) > 0:
            rnd_key = random.choice(froxly_free_proxy_keys)
            rnd_free_proxy = red.get(rnd_key)
        else:
            conn = orm.null_engine.connect()
            ses = orm.sescls(bind=conn)
            free_proxies = ses.query(orm.FreeProxy).filter(orm.and_(orm.FreeProxy.protocol == 'http',
                orm.FreeProxy.http_status == 200)).all()
            for free_proxy in free_proxies:
                red_key = red_keys.froxly_free_proxy + str(free_proxy.id)
                red_proxy = {'id': free_proxy.id, 'ip': free_proxy.ip, 'port': free_proxy.port,
                    'protocol': free_proxy.protocol}
                red.set(red_key, json.dumps(red_proxy))
                red.expire(red_key, expire_delta)
            ses.close()
            conn.close()
            rnd_key = random.choice(red.keys(red_keys.froxly_free_proxy + '*'))
            rnd_free_proxy = red.get(rnd_key)
        if rnd_free_proxy is not None:
            rnd_free_proxy_socket.send_unicode(json.dumps({'result': json.loads(rnd_free_proxy.decode('utf-8'))}))
        else:
            nlog.info('froxly - rnd free proxy error', 'Random free proxy is None')
    def activate(msg):
        pass
    def deactivate(msg):
        red_key = red_keys.froxly_free_proxy + str(msg['params']['proxy']['id'])
        red.delete(red_key)
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def list_for_domain(msg):
        checker.check(msg['params']['domain'])
        froxly_data_server_socket.send_unicode(json.dumps({'result': None}))
    def rnd_for_domain(msg):
        pass
    methods = {}
    methods[rnd.__name__] = rnd
    methods[activate.__name__] = activate
    methods[deactivate.__name__] = deactivate
    methods[list_for_domain.__name__] = list_for_domain
    methods[rnd_for_domain.__name__] = rnd_for_domain
    checker.init()
    while True:
        try:
            msg = json.loads(froxly_data_server_socket.recv_unicode())
            if msg['method'] in methods:
                methods[msg['method']](msg)
        except:
            nlog.info('froxly - data server error', traceback.format_exc())
except:
    nlog.info('froxly - data server fatal', traceback.format_exc())
    if ctx is not None:
        ctx.destroy()
    if ses is not None:
        ses.close()
    if conn is not None:    
        conn.close()