from urllib.error import *
from http.client import *
import multiprocessing
import traceback
import threading
import socket
import zmq
import json

import werp.froxly.errors
from werp import orm
from werp.orm import uatrains
from werp import nlog
from werp.uatrains.engine import drv
from werp.uatrains.bot import task_status
from werp.uatrains.bot import task_drvs
from werp.common import sockets
from werp.common import red_keys
from werp.froxly.data_server import common as data_server_common

try:
    ctx = zmq.Context()
    froxly_data_server_socket = ctx.socket(zmq.REQ)
    froxly_data_server_socket.connect(sockets.froxly_data_server)
    def run_task(task_id):
        try:
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
                try:
                    if task.drv == task_drvs.southwest:
                        drv.southwest.get_train_data(task.data)
                    elif task.drv == task_drvs.passengers:
                        drv.passengers.get_train_data(task.data)
                except werp.froxly.errors.ProxyError as e:
                    task.http_status_reason = str(e)
                    if e.proxy is not None:
                        if isinstance(e.base_exception, HTTPError):
                            task.http_status = -1
                        else:
                            task.http_status = -11
                            #domain = ''
                            #if task.drv == task_drvs.passengers:
                            #    domain = drv.passengers.domain
                            #else:
                            #    domain = drv.southwest.domain
                            #sproxy = data_server_common.jproxy2sproxy(e.proxy)
                            #froxly_data_server_socket.send_unicode(json.dumps({'method': 'deactivate_for_url', 'params':
                            #    {'url': domain, 'proxy': sproxy}}))
                            #froxly_data_server_socket.recv_unicode()
                except Exception as e:
                    task.http_status = -2
                    task.http_status_reason = str(e)
                    nlog.info('uatrains bot - task runner error', traceback.format_exc())
                if task.http_status is None:
                    task.http_status = 200
                task.status = task_status.completed
                ses.commit()
            ses.close()
            conn.close()
        except:
            nlog.info('uatrains bot - task runner error', traceback.format_exc())
    froxly_data_server_socket.send_unicode(json.dumps({'method': 'clear_for_url', 'params':
        {'url': drv.southwest.domain}}))
    froxly_data_server_socket.recv_unicode()
    froxly_data_server_socket.send_unicode(json.dumps({'method': 'clear_for_url', 'params':
        {'url': drv.passengers.domain}}))
    froxly_data_server_socket.recv_unicode()
    froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
        {'url': drv.southwest.domain}}))
    froxly_data_server_socket.recv_unicode()
    froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
        {'url': drv.passengers.domain}}))
    froxly_data_server_socket.recv_unicode()
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
    #for task_id in task_ids:
    #    thr = threading.Thread(target=run_task, args=(task_id,))
    #    thr.setDaemon(True)
    #    thr.start()
except:
    nlog.info('uatrains bot - task runner error', traceback.format_exc())