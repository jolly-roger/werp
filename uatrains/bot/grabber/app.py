import traceback
import threading
import time
import datetime
import zmq
import json

from werp import nlog, exec_log
from werp.common import sockets
from werp.uatrains.bot.grabber import task_drvs, worker, ventilator

try:
    ctx = zmq.Context()
    uatrains_bot_server_socket = ctx.socket(zmq.REP)
    uatrains_bot_server_socket.bind(sockets.uatrains_bot_server)
    def grab_etrain(msg):
        try:
            start_dt = datetime.datetime.now()
            start_time = time.time()
            ventilator.run(task_drvs.southwest, 16)
            end_time = time.time()
            exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
            exec_log.info('uatrains bot - task runner - etrain %s %s' % (str(start_dt), str(exec_delta)))
        except:
            nlog.info('uatrains bot - task runner - etrain - server error', traceback.format_exc())
    def grab_ptrain(msg):
        try:
            start_dt = datetime.datetime.now()
            start_time = time.time()
            ventilator.run(task_drvs.passengers, 32)
            end_time = time.time()
            exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
            exec_log.info('uatrains bot - task runner - ptrain %s %s' % (str(start_dt), str(exec_delta)))
        except:
            nlog.info('uatrains bot - task runner - ptrain - server error', traceback.format_exc())

    methods = {}
    methods[grab_etrain.__name__] = grab_etrain
    methods[grab_ptrain.__name__] = grab_ptrain
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