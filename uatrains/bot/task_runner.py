from urllib.error import *
from http.client import *
import multiprocessing
import traceback
import threading
import zmq
import json
import time
import datetime
import redis

from werp import orm
from werp.orm import uatrains
from werp import nlog
from werp.uatrains.engine import drv
from werp.uatrains.bot import task_status
from werp.uatrains.bot import task_drvs
from werp.common import sockets
from werp.common import red_keys

TRY_COUNT = 5

def run_task(task_id):
    conn = None
    ses = None
    try:
        ctx = zmq.Context()
        
        froxly_data_server_socket = ctx.socket(zmq.REQ)
        froxly_data_server_socket.connect(sockets.froxly_data_server)
        
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        task = None
        try:
            task = ses.query(uatrains.BotTask).filter(uatrains.BotTask.id == task_id).one()
        except:
            nlog.info('uatrains bot - task runner error', traceback.format_exc())
        if task is not None:
            task.status = task_status.running
            ses.commit()
            task.http_status = 0
            try_count = 0
            ua_res_data = None
            ru_res_data = None
            en_res_data = None
            while task.http_status <= 0 and try_count < TRY_COUNT:
                current_drv = None
                if task.drv == task_drvs.southwest:
                    current_drv = drv.southwest
                elif task.drv == task_drvs.passengers:
                    current_drv = drv.passengers
                if ua_res_data is None:
                    ua_url = current_drv.ua_url.replace('(tid)', str(task.data))
                    ua_req = {'method': 'request', 'params': {'url': ua_url, 'charset': current_drv.charset}}
                    froxly_data_server_socket.send_unicode(json.dumps(ua_req))
                    ua_res = json.loads(froxly_data_server_socket.recv_unicode())
                    if 'http_status' in ua_res['result'] and 'data' in ua_res['result'] and \
                        ua_res['result']['http_status'] == 200:
                        ua_res_data = ua_res['result']['data']
                    else:
                        task.http_status = ua_res['result']['http_status']
                        task.http_status_reason = ua_res['result']['http_status_reason']
                if ru_res_data is None:
                    ru_url = current_drv.ru_url.replace('(tid)', str(task.data))
                    ru_req = {'method': 'request', 'params': {'url': ru_url, 'charset': current_drv.charset}}
                    froxly_data_server_socket.send_unicode(json.dumps(ru_req))
                    ru_res = json.loads(froxly_data_server_socket.recv_unicode())
                    if 'http_status' in ru_res['result'] and 'data' in ru_res['result'] and \
                        ru_res['result']['http_status'] == 200:
                        ru_res_data = ru_res['result']['data']
                    else:
                        task.http_status = ua_res['result']['http_status']
                        task.http_status_reason = ua_res['result']['http_status_reason']
                if en_res_data is None:
                    en_url = current_drv.en_url.replace('(tid)', str(task.data))
                    en_req = {'method': 'request', 'params': {'url': en_url, 'charset': current_drv.charset}}
                    froxly_data_server_socket.send_unicode(json.dumps(en_req))
                    en_res = json.loads(froxly_data_server_socket.recv_unicode())
                    if 'http_status' in en_res['result'] and 'data' in en_res['result'] and \
                        en_res['result']['http_status'] == 200:
                        en_res_data = en_res['result']['data']
                    else:
                        task.http_status = ua_res['result']['http_status']
                        task.http_status_reason = ua_res['result']['http_status_reason']
                try:
                    if ua_res_data is not None and ru_res_data is not None and en_res_data is not None:
                        current_drv.get_train_data(task.data, ua_res_data, ru_res_data, en_res_data)
                        task.http_status = 200
                        task.http_status_reason = None
                except Exception as e:
                    task.http_status = -2
                    task.http_status_reason = str(e)
                    nlog.info('uatrains bot - task runner error', traceback.format_exc())
                try_count += 1
            task.status = task_status.completed
            ses.commit()
        ses.close()
        conn.close()
    except:
        nlog.info('uatrains bot - task runner error', traceback.format_exc())
        if ses is not None:
            ses.close()
        if conn is not None:    
            conn.close()

try:
    start_dt = datetime.datetime.now()
    start_time = time.time()
    conn = orm.null_engine.connect()
    ses = orm.sescls(bind=conn)
    tasks = ses.query(uatrains.BotTask).filter(uatrains.BotTask.status == None).all()
    task_ids = []
    for t in tasks:
        task_ids.append(t.id)
    ses.close()
    conn.close()
    with multiprocessing.Pool(processes=16) as ppool:
        ppool.map(run_task, [task_id for task_id in task_ids])
    end_time = time.time()
    exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
    red = redis.StrictRedis(unix_socket_path=sockets.redis)
    red.rpush(red_keys.exec_time_log, 'uatrains bot task runner %s %s' % (str(start_dt), str(exec_delta)))
except:
    nlog.info('uatrains bot - task runner error', traceback.format_exc())