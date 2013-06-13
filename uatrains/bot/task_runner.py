from urllib.error import *
from http.client import *
from lxml import etree
import io
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
            ua_dom_tree = None
            ru_dom_tree = None
            en_dom_tree = None
            current_drv = None
            parser = etree.HTMLParser()
            if task.drv == task_drvs.southwest:
                current_drv = drv.southwest
            elif task.drv == task_drvs.passengers:
                current_drv = drv.passengers
            while task.http_status <= 0 and try_count < TRY_COUNT:
                ua_res = None
                ru_res = None
                en_res = None
                if ua_dom_tree is None:
                    ua_url = current_drv.ua_url.replace('(tid)', str(task.data))
                    ua_req = {'method': 'request', 'params': {'url': ua_url, 'charset': current_drv.charset}}
                    froxly_data_server_socket.send_unicode(json.dumps(ua_req))
                    ua_res = json.loads(froxly_data_server_socket.recv_unicode())
                    if 'http_status' in ua_res['result'] and 'data' in ua_res['result'] and \
                        ua_res['result']['http_status'] == 200:
                        try:
                            ua_dom_tree = etree.parse(io.StringIO(ua_res['result']['data']), parser)
                        except Exception as e:
                            ua_res['result']['http_status'] = -3
                            ua_res['result']['http_status_reason'] = str(e)
                if ru_dom_tree is None:
                    ru_url = current_drv.ru_url.replace('(tid)', str(task.data))
                    ru_req = {'method': 'request', 'params': {'url': ru_url, 'charset': current_drv.charset}}
                    froxly_data_server_socket.send_unicode(json.dumps(ru_req))
                    ru_res = json.loads(froxly_data_server_socket.recv_unicode())
                    if 'http_status' in ru_res['result'] and 'data' in ru_res['result'] and \
                        ru_res['result']['http_status'] == 200:
                        try:
                            ru_dom_tree = etree.parse(io.StringIO(ru_res['result']['data']), parser)
                        except Exception as e:
                            ru_res['result']['http_status'] = -3
                            ru_res['result']['http_status_reason'] = str(e)
                if en_dom_tree is None:
                    en_url = current_drv.en_url.replace('(tid)', str(task.data))
                    en_req = {'method': 'request', 'params': {'url': en_url, 'charset': current_drv.charset}}
                    froxly_data_server_socket.send_unicode(json.dumps(en_req))
                    en_res = json.loads(froxly_data_server_socket.recv_unicode())
                    if 'http_status' in en_res['result'] and 'data' in en_res['result'] and \
                        en_res['result']['http_status'] == 200:
                        try:
                            en_dom_tree = etree.parse(io.StringIO(en_res['result']['data']), parser)
                        except Exception as e:
                            en_res['result']['http_status'] = -3
                            en_res['result']['http_status_reason'] = str(e)
                if ua_res is not None and 'http_status' in ua_res['result'] and ua_res['result']['http_status'] < 0:
                    task.http_status = ua_res['result']['http_status']
                    task.http_status_reason = ua_res['result']['http_status_reason']
                if ru_res is not None and 'http_status' in ru_res['result'] and ru_res['result']['http_status'] < 0:
                    task.http_status = ru_res['result']['http_status']
                    task.http_status_reason = ru_res['result']['http_status_reason']
                if en_res is not None and 'http_status' in en_res['result'] and en_res['result']['http_status'] < 0:
                    task.http_status = en_res['result']['http_status']
                    task.http_status_reason = en_res['result']['http_status_reason']
                try:
                    if ua_dom_tree is not None and ru_dom_tree is not None and en_dom_tree is not None:
                        current_drv.get_train_data(int(task.data), ua_dom_tree, ru_dom_tree, en_dom_tree)
                        task.http_status = 200
                        task.http_status_reason = None
                except Exception as e:
                    task.http_status = -2
                    task.http_status_reason = str(e)
                    nlog.info('uatrains bot - task runner error', 'Task data: ' + str(task.data) + '\n\n' + \
                        traceback.format_exc())
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
    red = redis.StrictRedis(unix_socket_path=sockets.redis)
    red.delete(red_keys.uatrains_bot_log)
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
    with multiprocessing.Pool(processes=8) as ppool:
        ppool.map(run_task, [task_id for task_id in task_ids])
    end_time = time.time()
    exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
    red.rpush(red_keys.exec_time_log, 'uatrains bot task runner %s %s' % (str(start_dt), str(exec_delta)))
except:
    nlog.info('uatrains bot - task runner error', traceback.format_exc())