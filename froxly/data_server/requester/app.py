import traceback
import threading

from werp import nlog
from werp.froxly.data_server.requester import worker

WORKER_POOL = 32

try:
    for wrk_num in range(WORKER_POOL):
        thr = threading.Thread(target=worker.run)
        thr.start()
except:
    nlog.info('froxly - requester server fatal', traceback.format_exc())