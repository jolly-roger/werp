import urllib.request
import traceback
import zmq
import json

from werp import nlog
from werp.common import sockets
from werp.common import timeouts
from werp.common import red_keys

def run():
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
    except:
        nlog.info('froxly - checher error', traceback.format_exc())