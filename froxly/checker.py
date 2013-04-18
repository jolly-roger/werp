from urllib.error import *
from http.client import *
import socket 
import urllib.request
import traceback
import errno
import os
import zmq
import json
import threading
import time
import redis

from werp import orm
from werp import nlog

test_url = 'http://user-agent-list.com/'
red_key_prfix = 'froxly_free_proxy_'
worker_pool = 16

def ventilator():
    conn = None
    ses = None
    ctx = None
    try:
        ctx = zmq.Context()
        froxly_checker_req = ctx.socket(zmq.PUSH)
        froxly_checker_req.bind('ipc:///home/www/sockets/froxly_checker_req.socket')
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        proxies = ses.query(orm.FreeProxy).filter(orm.FreeProxy.protocol == 'http').all()
        for proxy in proxies:
            wproxy = {'id': proxy.id, 'ip': proxy.ip, 'port': proxy.port, 'protocol': proxy.protocol}
            froxly_checker_req.send_unicode(json.dumps(wproxy))
        froxly_checker_finish = ctx.socket(zmq.REQ)
        froxly_checker_finish.connect('ipc:///home/www/sockets/froxly_checker_finish.socket')
        froxly_checker_finish.send_unicode(str(len(proxies)))
        froxly_checker_finish.recv_unicode()
        ctx.destroy()
        ses.close()
        conn.close()
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
        if ctx is not None:
            ctx.destroy()
        if ses is not None:
            ses.close()
        if conn is not None:    
            conn.close()
def worker():
    ctx = None
    try:
        ctx = zmq.Context()
        froxly_checker_req = ctx.socket(zmq.PULL)
        froxly_checker_req.connect('ipc:///home/www/sockets/froxly_checker_req.socket')
        rnd_user_agent_socket = ctx.socket(zmq.REQ)
        rnd_user_agent_socket.connect('ipc:///home/www/sockets/rnd_user_agent.socket')
        froxly_checker_res = ctx.socket(zmq.PUSH)
        froxly_checker_res.connect('ipc:///home/www/sockets/froxly_checker_res.socket')
        while True:
            wproxy = json.loads(froxly_checker_req.recv_unicode())
            rnd_user_agent_socket.send_unicode('')
            rnd_user_agent = rnd_user_agent_socket.recv_unicode()
            req = urllib.request.Request(test_url, headers={'User-Agent': rnd_user_agent}, method='HEAD')
            req.set_proxy(wproxy['ip'] + ':' + wproxy['port'], wproxy['protocol'])
            try:
                res = urllib.request.urlopen(req, timeout=30)
                if res.getcode() == 200:
                    wproxy['http_status'] = res.getcode()
                    wproxy['http_status_reason'] = None
            except socket.timeout as e:
                wproxy['http_status'] = -6
                wproxy['http_status_reason'] = str(e)
            except BadStatusLine as e:
                wproxy['http_status'] = -5
                wproxy['http_status_reason'] = str(e)
            except URLError as e:
                wproxy['http_status'] = -4
                wproxy['http_status_reason'] = str(e)
            except HTTPError as e:
                wproxy['http_status'] = -3
                wproxy['http_status_reason'] = str(e)
            except ConnectionError as e:
                wproxy['http_status'] = -2
                wproxy['http_status_reason'] = str(e)
            except:
                wproxy['http_status'] = -1
                wproxy['http_status_reason'] = str(e)
                nlog.info('froxly - checker request error', traceback.format_exc())
            froxly_checker_res.send_unicode(json.dumps(wproxy))
        ctx.destroy()
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
        if ctx is not None:
            ctx.destroy()
def result_manager():
    conn = None
    ses = None
    ctx = None
    try:
        red = redis.StrictRedis(unix_socket_path='/tmp/redis.socket')
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        ctx = zmq.Context()
        froxly_checker_res = ctx.socket(zmq.PULL)
        froxly_checker_res.bind('ipc:///home/www/sockets/froxly_checker_res.socket')
        froxly_checker_finish = ctx.socket(zmq.REP)
        froxly_checker_finish.bind('ipc:///home/www/sockets/froxly_checker_finish.socket')
        proxy_count = int(froxly_checker_finish.recv_unicode())
        while True:
            wproxy = json.loads(froxly_checker_res.recv_unicode())
            proxy = ses.query(orm.FreeProxy).filter(orm.FreeProxy.id == wproxy['id']).one()
            proxy.http_status = wproxy['http_status']
            proxy.http_status_reason = wproxy['http_status_reason']
            ses.commit()
            red_key = red_key_prfix + str(wproxy['id'])
            if not red.exists(red_key):
                if wproxy['http_status'] == 200:
                    del wproxy['id']
                    del wproxy['http_status']
                    del wproxy['http_status_reason']
                    red.set(red_key, json.dumps(wproxy))
                else:
                    red.delete(red_key)
            proxy_count = proxy_count - 1
            if proxy_count == 0:
                break
        froxly_checker_finish.send_unicode(str(0))
        ctx.destroy()
        ses.close()
        conn.close()
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
        if ctx is not None:
            ctx.destroy()
        if ses is not None:
            ses.close()
        if conn is not None:    
            conn.close()
try:
    nlog.info('froxly - checher ventilator', 'Hi!!!')
    for wrk_num in range(worker_pool):
        thr = threading.Thread(target=worker)
        thr.setDaemon(True)
        thr.start()
    result_manager = threading.Thread(target=result_manager)
    result_manager.setDaemon(True)
    result_manager.start()
    ventilator()
    nlog.info('froxly - checher ventilator', 'Yo!!!')
except:
    nlog.info('froxly - checher error', traceback.format_exc())