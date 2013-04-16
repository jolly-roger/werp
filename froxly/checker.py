import urllib.request
from urllib.error import *
import random
import traceback
import errno
import os
import zmq

from werp import orm
from werp import nlog

test_url = 'http://user-agent-list.com/'

try:
    context = zmq.Context()
    rnd_user_agent_socket = context.socket(zmq.REQ)
    rnd_user_agent_socket.connect('ipc:///home/www/sockets/rnd_user_agent.socket')
    
    while True:
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        proxies = ses.query(orm.FreeProxy).filter(orm.FreeProxy.protocol == 'http').all()
        for proxy in proxies:
            rnd_user_agent_socket.send_unicode('')
            rnd_user_agent = rnd_user_agent_socket.recv_unicode()
            req = urllib.request.Request(test_url, headers={'User-Agent': rnd_user_agent})
            req.set_proxy(proxy.ip + ':' + proxy.port, proxy.protocol)
            try:
                res = urllib.request.urlopen(req)
                if res.getcode() == 200:
                    nlog.info('froxly - checker request debug', 'Yo!!!')
                    
                    proxy.http_status = res.getcode()
                    proxy.http_status_reason = None
            except URLError as e:
                proxy.http_status = -3
                proxy.http_status_reason = str(e.reason)
            except HTTPError as e:
                proxy.http_status = e.code
                proxy.http_status_reason = str(e.reason)
            except ConnectionError as e:
                proxy.http_status = -2
                proxy.http_status_reason = '[Errno ' + str(e.errno) + '] ' + os.strerror(e.errno)
            except:
                proxy.http_status = -1
                proxy.http_status_reason = None
                nlog.info('froxly - checker request error', traceback.format_exc())
            ses.commit()
        ses.close()
        conn.close()
except:
    nlog.info('froxly - checher error', traceback.format_exc())