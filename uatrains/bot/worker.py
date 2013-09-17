from urllib.error import *
from http.client import *
from lxml import etree
import io
import traceback
import zmq
import json

from werp.uatrains import bot
from werp import orm
from werp.uatrains.engine import drv
from werp.uatrains.bot import task_status
from werp.uatrains.bot import task_drvs
from werp.common import sockets

TRY_COUNT = 11
REQ_TIMEOUT = 33

def run(task_drv):
    conn = None
    ses = None
    try:
        ctx = zmq.Context()
        
        froxly_data_server_socket = ctx.socket(zmq.REQ)
        froxly_data_server_socket.connect(sockets.format_socket_uri(sockets.froxly_data_server, drv=task_drv))
        
        uatrains_bot_task_sink_socket = ctx.socket(zmq.PUSH)
        uatrains_bot_task_sink_socket.connect(sockets.format_socket_uri(sockets.uatrains_bot_task_sink, drv=task_drv))
        
        uatrains_bot_task_worker_socket = ctx.socket(zmq.PULL)
        uatrains_bot_task_worker_socket.connect(sockets.format_socket_uri(sockets.uatrains_bot_task_worker, drv=task_drv))
        
        uatrains_bot_task_finish_socket = ctx.socket(zmq.SUB)
        uatrains_bot_task_finish_socket.connect(sockets.format_socket_uri(sockets.uatrains_bot_task_finish, drv=task_drv))
        uatrains_bot_task_finish_socket.setsockopt_string(zmq.SUBSCRIBE, '')
        
        poller = zmq.Poller()
        poller.register(uatrains_bot_task_worker_socket, zmq.POLLIN)
        poller.register(uatrains_bot_task_finish_socket, zmq.POLLIN)
        
        conn = orm.null_engine.connect()

        while True:
            socks = dict(poller.poll())

            if uatrains_bot_task_worker_socket in socks and socks[uatrains_bot_task_worker_socket] == zmq.POLLIN:
                ses = orm.sescls(bind=conn)
                
                task_id = uatrains_bot_task_worker_socket.recv_unicode()
            
                task = None
                try:
                    task = ses.query(orm.uatrains.BotTask).filter(orm.uatrains.BotTask.id == task_id).one()
                except:
                    bot.logger.error('uatrains bot - task worker error\r\n' + traceback.format_exc())
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
                            ua_req = {'method': 'request', 'params': {'url': ua_url, 'charset': current_drv.charset,
                                'timeout': REQ_TIMEOUT}}
                            froxly_data_server_socket.send_unicode(json.dumps(ua_req))
                            ua_res = json.loads(froxly_data_server_socket.recv_unicode())
                            if 'http_status' in ua_res['result'] and 'data' in ua_res['result'] and \
                                ua_res['result']['http_status'] == 200:
                                try:
                                    ua_dom_tree = etree.parse(io.StringIO(ua_res['result']['data']), parser)
                                    ua_dom_tree.xpath('/html')
                                except Exception as e:
                                    ua_res['result']['http_status'] = -3
                                    ua_res['result']['http_status_reason'] = str(e)
                        if ru_dom_tree is None:
                            ru_url = current_drv.ru_url.replace('(tid)', str(task.data))
                            ru_req = {'method': 'request', 'params': {'url': ru_url, 'charset': current_drv.charset,
                                'timeout': REQ_TIMEOUT}}
                            froxly_data_server_socket.send_unicode(json.dumps(ru_req))
                            ru_res = json.loads(froxly_data_server_socket.recv_unicode())
                            if 'http_status' in ru_res['result'] and 'data' in ru_res['result'] and \
                                ru_res['result']['http_status'] == 200:
                                try:
                                    ru_dom_tree = etree.parse(io.StringIO(ru_res['result']['data']), parser)
                                    ru_dom_tree.xpath('/html')
                                except Exception as e:
                                    ru_res['result']['http_status'] = -3
                                    ru_res['result']['http_status_reason'] = str(e)
                        if en_dom_tree is None:
                            en_url = current_drv.en_url.replace('(tid)', str(task.data))
                            en_req = {'method': 'request', 'params': {'url': en_url, 'charset': current_drv.charset,
                                'timeout': REQ_TIMEOUT}}
                            froxly_data_server_socket.send_unicode(json.dumps(en_req))
                            en_res = json.loads(froxly_data_server_socket.recv_unicode())
                            if 'http_status' in en_res['result'] and 'data' in en_res['result'] and \
                                en_res['result']['http_status'] == 200:
                                try:
                                    en_dom_tree = etree.parse(io.StringIO(en_res['result']['data']), parser)
                                    en_dom_tree.xpath('/html')
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
                                drv.get_train_data(current_drv, int(task.data), ua_dom_tree, ru_dom_tree, en_dom_tree)
                                task.http_status = 200
                                task.http_status_reason = None
                        except Exception as e:
                            task.http_status = -2
                            task.http_status_reason = str(e)
                            bot.logger.error('uatrains bot - task worker error\r\n' + 'Task data: ' + \
                                str(task.data) + '\n\n' + traceback.format_exc())
                        try_count += 1
                    task.status = task_status.completed
                    ses.commit()
                    ses.close()
                    uatrains_bot_task_sink_socket.send_unicode(str(1))
            
            if uatrains_bot_task_finish_socket in socks and socks[uatrains_bot_task_finish_socket] == zmq.POLLIN:
                break
        
        conn.close()
    except:
        bot.logger.error('uatrains bot - task worker error\r\n' + traceback.format_exc())
        if ses is not None:
            ses.close()
        if conn is not None:    
            conn.close()