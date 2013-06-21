import traceback
import threading
import time
import datetime
import redis
import zmq
import json

from werp import nlog
from werp.common import sockets
from werp.common import red_keys
from werp.uatrains.bot import worker
from werp.uatrains.bot import ventilator

try:
    ctx = zmq.Context()
    uatrains_bot_server_socket = ctx.socket(zmq.REP)
    uatrains_bot_server_socket.bind(sockets.uatrains_bot_server)
    def grab(msg):
        try:
            start_dt = datetime.datetime.now()
            start_time = time.time()
            ventilator.run()
            end_time = time.time()
            exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
            red = redis.StrictRedis(unix_socket_path=sockets.redis)
            red.rpush(red_keys.exec_time_log, 'uatrains bot task runner %s %s' % (str(start_dt), str(exec_delta)))
        except:
            nlog.info('uatrains bot - server error', traceback.format_exc())

    methods = {}
    methods[grab.__name__] = grab
    while True:
        try:
            msg = json.loads(uatrains_bot_server_socket.recv_unicode())
            if msg['method'] in methods:
                thr = threading.Thread(target=methods[msg['method']], args=(msg,))
                thr.start()
        except:
            nlog.info('uatrains bot - server error', traceback.format_exc())
        uatrains_bot_server_socket.send_unicode(json.dumps({'result': None}))
except:
    nlog.info('uatrains bot - server fatal', traceback.format_exc())