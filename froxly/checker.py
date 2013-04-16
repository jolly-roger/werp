import urllib.request
from urllib.error import *
import random
import traceback
import errno

from werp import orm
from werp import nlog

test_url = 'http://user-agent-list.com/'

try:
    while True:
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        proxies = ses.query(orm.FreeProxy).filter(orm.FreeProxy.protocol == 'http').all()
        user_agents = ses.query(orm.UserAgent).filter(orm.UserAgent.is_bot == False).all()
        for proxy in proxies:
            rnd_user_agent = random.choice(user_agents)
            req = urllib.request.Request(test_url, headers={'User-Agent': rnd_user_agent.value})
            req.set_proxy(proxy.ip + ':' + proxy.port, proxy.protocol)
            try:
                res = urllib.request.urlopen(req)
                if res.getcode() == 200:
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
                proxy.http_status_reason = '[Errno ' + str(e.errno) + '] ' + errno.errorcode[e.errno]
            except:
                proxy.http_status = -1
                proxy.http_status_reason = None
                nlog.info('froxly - checker request error', traceback.format_exc())
            ses.commit()
        ses.close()
        conn.close()
except:
    nlog.info('froxly - checher error', traceback.format_exc())