import datetime
import zmq
import traceback
import redis
import random
import json

from werp import orm
from werp import nlog

expire_delta = datetime.timedelta(days=1)
red_key_prfix = 'froxly_free_proxy_'
conn = None
ses = None
ctx = None
try:
    ctx = zmq.Context()
    rnd_free_proxy_socket = ctx.socket(zmq.REP)
    rnd_free_proxy_socket.bind('ipc:///home/www/sockets/rnd_free_proxy.socket')
    red = redis.StrictRedis(unix_socket_path='/tmp/redis.socket')
    while True:
        msg = rnd_free_proxy_socket.recv_unicode()
        red_keys = red.keys(red_key_prfix + '*')
        rnd_free_proxy = None
        if len(red_keys) > 0:
            rnd_key = random.choice(red_keys)
            rnd_free_proxy = red.get(rnd_key)
        else:
            conn = orm.null_engine.connect()
            ses = orm.sescls(bind=conn)
            free_proxies = ses.query(orm.FreeProxy).filter(orm.and_(orm.FreeProxy.protocol == 'http',
                orm.FreeProxy.http_status == 200)).all()
            for free_proxy in free_proxies:
                red_key = red_key_prfix + str(free_proxy.id)
                red_proxy = {'ip': free_proxy.ip, 'port': free_proxy.port, 'protocol': free_proxy.protocol}
                red.set(red_key, json.dumps(red_proxy))
                red.expire(red_key, expire_delta)
            ses.close()
            conn.close()
            rnd_key = random.choice(red.keys(red_key_prfix + '*'))
            rnd_free_proxy = red.get(rnd_key)
        if rnd_free_proxy is not None:
            rnd_free_proxy_socket.send_unicode(rnd_free_proxy.decode('utf-8'))
        else:
            nlog.info('froxly - rnd free proxy error', 'Random free proxy is None')
except:
    nlog.info('froxly - rnd free proxy error', traceback.format_exc())
    if ctx is not None:
        ctx.destroy()
    if ses is not None:
        ses.close()
    if conn is not None:    
        conn.close()