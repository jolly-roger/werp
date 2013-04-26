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
import datetime
import redis

from werp import orm
from werp import nlog
from werp.common import sockets
from werp.common import timeouts
from werp.common import red_keys

worker_pool = 16
expire_delta = datetime.timedelta(days=1)

def ventilator(url):
    conn = None
    ses = None
    ctx = None
    try:
        ctx = zmq.Context()
        froxly_checker_req = ctx.socket(zmq.PUSH)
        froxly_checker_req.bind(sockets.froxly_checker_req)
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        proxies = ses.query(orm.FreeProxy).filter(orm.FreeProxy.protocol == 'http').all()
        for proxy in proxies:
            task = {'url': url, 'proxy': {'id': proxy.id, 'ip': proxy.ip, 'port': proxy.port,
                'protocol': proxy.protocol}}
            froxly_checker_req.send_unicode(json.dumps(task))
        froxly_checker_finish = ctx.socket(zmq.REQ)
        froxly_checker_finish.connect(sockets.froxly_checker_finish)
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
        froxly_checker_req.connect(sockets.froxly_checker_req)
        rnd_user_agent_socket = ctx.socket(zmq.REQ)
        rnd_user_agent_socket.connect(sockets.rnd_user_agent)
        froxly_checker_res = ctx.socket(zmq.PUSH)
        froxly_checker_res.connect(sockets.froxly_checker_res)
        while True:
            task = json.loads(froxly_checker_req.recv_unicode())
            rnd_user_agent_socket.send_unicode('')
            rnd_user_agent = rnd_user_agent_socket.recv_unicode()
            req = urllib.request.Request(task['url'], headers={'User-Agent': rnd_user_agent})#, method='HEAD')
            req.set_proxy(task['proxy']['ip'] + ':' + task['proxy']['port'], task['proxy']['protocol'])
            try:
                res = urllib.request.urlopen(req, timeout=timeouts.froxly_checker)
                res.read()
                if res.getcode() == 200:
                    task['proxy']['http_status'] = res.getcode()
                    task['proxy']['http_status_reason'] = None
            except Exception as e:
                task['proxy']['http_status'] = -1
                task['proxy']['http_status_reason'] = str(e)
            froxly_checker_res.send_unicode(json.dumps(task))
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
        red = redis.StrictRedis(unix_socket_path=sockets.redis)
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        ctx = zmq.Context()
        froxly_checker_res = ctx.socket(zmq.PULL)
        froxly_checker_res.bind(sockets.froxly_checker_res)
        froxly_checker_finish = ctx.socket(zmq.REP)
        froxly_checker_finish.bind(sockets.froxly_checker_finish)
        proxy_count = int(froxly_checker_finish.recv_unicode())
        while True:
            task = json.loads(froxly_checker_res.recv_unicode())
            proxy = ses.query(orm.FreeProxy).filter(orm.FreeProxy.id == task['proxy']['id']).one()
            proxy.http_status = task['proxy']['http_status']
            proxy.http_status_reason = task['proxy']['http_status_reason']
            ses.commit()
            red_key = red_keys.froxly_free_proxy + task['url'] + '_' + str(task['proxy']['id'])
            if not red.exists(red_key):
                if task['proxy']['http_status'] == 200:
                    del task['proxy']['http_status']
                    del task['proxy']['http_status_reason']
                    red.set(red_key, json.dumps(task['proxy']))
                    red.expire(red_key, expire_delta)
            else:
                if task['proxy']['http_status'] != 200:
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
def check(url = 'http://user-agent-list.com'):
    try:
        start_time = time.time()
        ventilator(url)
        end_time = time.time()
        exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
        nlog.info('froxly - checher ventilator', str(exec_delta))
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
def init():
    try:
       for wrk_num in range(worker_pool):
           thr = threading.Thread(target=worker)
           thr.start()
       manager = threading.Thread(target=result_manager)
       manager.start()
    except:
       nlog.info('froxly - checher error', traceback.format_exc())