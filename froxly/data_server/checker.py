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

def ventilator():
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
            wproxy = {'id': proxy.id, 'ip': proxy.ip, 'port': proxy.port, 'protocol': proxy.protocol}
            froxly_checker_req.send_unicode(json.dumps(wproxy))
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
def worker(url):
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
            wproxy = json.loads(froxly_checker_req.recv_unicode())
            rnd_user_agent_socket.send_unicode('')
            rnd_user_agent = rnd_user_agent_socket.recv_unicode()
            req = urllib.request.Request(url, headers={'User-Agent': rnd_user_agent})#, method='HEAD')
            req.set_proxy(wproxy['ip'] + ':' + wproxy['port'], wproxy['protocol'])
            try:
                res = urllib.request.urlopen(req, timeout=timeouts.froxly_checker)
                res.read()
                if res.getcode() == 200:
                    wproxy['http_status'] = res.getcode()
                    wproxy['http_status_reason'] = None
            except Exception as e:
                wproxy['http_status'] = -1
                wproxy['http_status_reason'] = str(e)
            froxly_checker_res.send_unicode(json.dumps(wproxy))
        ctx.destroy()
    except:
        nlog.info('froxly - checher error', traceback.format_exc())
        if ctx is not None:
            ctx.destroy()
def result_manager(url, red_key_prefix):
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
            wproxy = json.loads(froxly_checker_res.recv_unicode())
            proxy = ses.query(orm.FreeProxy).filter(orm.FreeProxy.id == wproxy['id']).one()
            proxy.http_status = wproxy['http_status']
            proxy.http_status_reason = wproxy['http_status_reason']
            ses.commit()
            red_key = red_key_prefix + url + '_' + str(wproxy['id'])
            if not red.exists(red_key):
                if wproxy['http_status'] == 200:
                    del wproxy['http_status']
                    del wproxy['http_status_reason']
                    red.set(red_key, json.dumps(wproxy))
                    red.expire(red_key, expire_delta)
            else:
                if wproxy['http_status'] != 200:
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
        for wrk_num in range(worker_pool):
            thr = threading.Thread(target=worker, args=(url,))
            thr.setDaemon(True)
            thr.start()
        result_manager = threading.Thread(target=result_manager, args=(url, red_keys.froxly_free_proxy))
        result_manager.setDaemon(True)
        result_manager.start()
        ventilator()
        end_time = time.time()
        exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
        nlog.info('froxly - checher ventilator', str(exec_delta))
    except:
        nlog.info('froxly - checher error', traceback.format_exc())