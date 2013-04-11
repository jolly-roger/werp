from random import randint
import time
import zmq
import urllib.request
import random
import traceback

from werp import orm
from werp import nlog


LRU_READY = "\x01"

context = zmq.Context(1)
worker = context.socket(zmq.REQ)

identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
worker.setsockopt_unicode(zmq.IDENTITY, identity)
worker.connect("tcp://127.0.0.1:5556")
worker.send_unicode(LRU_READY)

cycles = 0
while True:
    try:
        msg = worker.recv_multipart()
        if not msg:
            break
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        url = msg[2].decode('utf-8')
        res = ''
        try_count = 0
        while res is '' and try_count < 11:
            proxies = ses.query(orm.FreeProxy).filter(orm.FreeProxy.protocol == 'http').all()
            user_agents = ses.query(orm.UserAgent).filter(orm.UserAgent.is_bot == False).all()
            rnd_proxy = random.choice(proxies)
            rnd_user_agent = random.choice(user_agents)
            req = urllib.request.Request(url, headers={'User-Agent': rnd_user_agent.value})
            req.set_proxy(rnd_proxy.ip + ':' + rnd_proxy.port, rnd_proxy.protocol)
            try:
                res = urllib.request.urlopen(req)
                if res.getcode() != 200:
                    res = ''
            except:
                nlog.info('froxly - zw', traceback.format_exc())
                res = ''
            try_count = try_count + 1
        ses.close()
        conn.close()
        worker.send_multipart(msg)
    except:
        nlog.info('froxly - zw', traceback.format_exc())