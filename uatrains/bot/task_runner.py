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

TRY_COUNT = 5

def run_task(task_id):
    try:
        ctx = zmq.Context()
        rnd_user_agent_socket = ctx.socket(zmq.REQ)
        rnd_user_agent_socket.connect(sockets.rnd_user_agent)
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
            
            nlog.info('uatrains bot - task runner info', '0')
            
            task.status = task_status.running
            ses.commit()
            task.http_status = 0
            #try_count = 0
            #while task.http_status <= 0 and try_count < TRY_COUNT:
            rnd_user_agent_socket.send_unicode('')
            rnd_user_agent = rnd_user_agent_socket.recv_unicode()
            froxly_data_server_socket.send_unicode(json.dumps({'method': 'rnd', 'params': None}))
            rnd_proxy_res = json.loads(froxly_data_server_socket.recv_unicode())
            rnd_proxy = None
            if rnd_proxy_res is not None:
                rnd_proxy = rnd_proxy_res['result']
            exc = None
            
            nlog.info('uatrains bot - task runner info', '1')
            
            try:
                if task.drv == task_drvs.southwest:
                    drv.southwest.get_train_data(task.data, rnd_proxy, rnd_user_agent)
                elif task.drv == task_drvs.passengers:
                    drv.passengers.get_train_data(task.data, rnd_proxy, rnd_user_agent)
            except werp.froxly.errors.ProxyError as e:
                
                nlog.info('uatrains bot - task runner info', traceback.format_exc())
                
                exc = e
                task.http_status_reason = str(e)
                if e.proxy is not None:
                    if isinstance(e.base_exception, HTTPError):
                        task.http_status = -1
                    else:
                        task.http_status = -11
                        domain = ''
                        if task.drv == task_drvs.passengers:
                            domain = drv.passengers.domain
                        else:
                            domain = drv.southwest.domain
                        sproxy = data_server_common.jproxy2sproxy(e.proxy)
                        froxly_data_server_socket = ctx.socket(zmq.REQ)
                        froxly_data_server_socket.connect(sockets.froxly_data_server)
                        froxly_data_server_socket.send_unicode(json.dumps({'method': 'deactivate_for_url', 'params':
                            {'url': domain, 'proxy': sproxy}}))
                        froxly_data_server_socket.recv_unicode()
            except Exception as e:
                exc = e
                task.http_status = -2
                task.http_status_reason = str(e)
                nlog.info('uatrains bot - task runner error', traceback.format_exc())
            if exc is None:
                task.http_status = 200
            
            nlog.info('uatrains bot - task runner info', '100')    
            
            #try_count += 1
            task.status = task_status.completed
            ses.commit()
        ses.close()
        conn.close()
    except:
        nlog.info('uatrains bot - task runner error', traceback.format_exc())

try:
    #ctx = zmq.Context()
    #froxly_data_server_socket = ctx.socket(zmq.REQ)
    #froxly_data_server_socket.connect(sockets.froxly_data_server)
    #froxly_data_server_socket.send_unicode(json.dumps({'method': 'clear_for_url', 'params':
    #    {'url': drv.southwest.domain}}))
    #froxly_data_server_socket.recv_unicode()
    #froxly_data_server_socket.send_unicode(json.dumps({'method': 'clear_for_url', 'params':
    #    {'url': drv.passengers.domain}}))
    #froxly_data_server_socket.recv_unicode()
    #froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
    #    {'url': drv.southwest.domain}}))
    #froxly_data_server_socket.recv_unicode()
    #froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
    #    {'url': drv.passengers.domain}}))
    #froxly_data_server_socket.recv_unicode()
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
except:
    nlog.info('uatrains bot - task runner error', traceback.format_exc())