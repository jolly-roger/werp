import traceback
import threading
import time
import datetime
import zmq
import json

from werp import froxly_checker_log
from werp.common import sockets
from werp.froxly.data_server.checker import ventilator

try:
    def base_check(msg):
        try:
            start_dt = datetime.datetime.now()
            froxly_grafroxly_checker_logbber_log.info('"base_check" is started at %s' % (str(start_dt), ))
            start_time = time.time()
            ventilator.base_run('http://user-agent-list.com')
            end_time = time.time()
            exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
            froxly_checker_log.info('"base_check" is finished, duration is %s \n\n' % (str(exec_delta),))
        except:
            froxly_checker_log.exception('app "base_check"\n\n' + traceback.format_exc())
    def url_check(msg):
        try:
            start_dt = datetime.datetime.now()
            froxly_grafroxly_checker_logbber_log.info('"url_check" is started at %s' % (str(start_dt), ))
            start_time = time.time()
            ventilator.url_run(msg['params']['url'],
                msg['params']['worker_pool'] if 'worker_pool' in msg['params'] else None,
                msg['params']['to_check_key'] if 'to_check_key' in msg['params'] else None)
            end_time = time.time()
            exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
            froxly_checker_log.info('"url_check" for url ' + msg['params']['url'] +\
                ' is finished, duration is %s \n\n' % (str(exec_delta),))
        except:
            froxly_checker_log.exception('app "url_check"\n\n' + traceback.format_exc())
    
    methods = {}
    methods[base_check.__name__] = base_check
    methods[url_check.__name__] = url_check
    
    ctx = zmq.Context()
    
    froxly_checker_server_socket = ctx.socket(zmq.PULL)
    froxly_checker_server_socket.bind(sockets.froxly_checker_server)
    
    while True:
        try:
            msg = json.loads(froxly_checker_server_socket.recv_unicode())
            if msg['method'] in methods:
                thr = threading.Thread(target=methods[msg['method']], args=(msg,))
                thr.start()
        except:
            froxly_checker_log.exception("app\n\n" + traceback.format_exc())
except:
    froxly_checker_log.fatal("app\n\n" + traceback.format_exc())