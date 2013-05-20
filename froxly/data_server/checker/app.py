import traceback
import threading
import time
import datetime
import redis

from werp import nlog
from werp.common import sockets
from werp.common import red_keys
from werp.froxly.data_server.checker import worker
from werp.froxly.data_server.checker import sink
from werp.froxly.data_server.checker import ventilator

worker_pool = 32

def base_check(url = 'http://user-agent-list.com'):
    try:
        ventilator.base_run(url)
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
def url_check(url = 'http://user-agent-list.com'):
    try:
        start_dt = datetime.datetime.now()
        start_time = time.time()
        ventilator.url_run(url)
        end_time = time.time()
        exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
        red = redis.StrictRedis(unix_socket_path=sockets.redis)
        red.rpush(red_keys.exec_time_log, 'froxly url (' + url + ') check %s %s' % (str(start_dt), str(exec_delta)))
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
def init():
    try:
       for wrk_num in range(worker_pool):
           thr = threading.Thread(target=worker.run)
           thr.start()
       manager = threading.Thread(target=sink.run)
       manager.start()
    except:
       nlog.info('froxly - checher error', traceback.format_exc())