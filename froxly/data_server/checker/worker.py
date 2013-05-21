import urllib.request
import urllib.parse
import traceback
import zmq
import json
import socket

from werp import nlog
from werp.common import sockets
from werp.common import timeouts
from werp.common import red_keys
from werp.thirdparty import socks

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
            try:
                s = socks.socksocket()
                s.settimeout(timeouts.froxly_checker)
                url_obj = urllib.parse.urlparse(task['url'])
                s.setproxy(socks.PROXY_TYPE_HTTP, task['proxy']['ip'], int(task['proxy']['port']))
                s.connect((url_obj.netloc, 80))
                req_path = '/'
                if url_obj.path is not None and url_obj.path != '':
                    req_path = url_obj.path
                req_str = 'GET ' + req_path + ' HTTP/1.1\r\nHost:' + url_obj.netloc + '\r\n\r\n'
                s.send(req_str.encode())
                res = s.recv(15).decode()
                #s.shutdown(socket.SHUT_RDWR)
                #s.close()
                if res == 'HTTP/1.1 200 OK' or res == 'HTTP/1.0 200 OK':
                    task['proxy']['http_status'] = 200
                    task['proxy']['http_status_reason'] = None
                else:
                    nlog.info('froxly - checher worker response info', res)
                    task['proxy']['http_status'] = -1
                    task['proxy']['http_status_reason'] = res
            except Exception as e:
                task['proxy']['http_status'] = -1
                task['proxy']['http_status_reason'] = str(e)
            froxly_checker_res.send_unicode(json.dumps(task))
    except:
        nlog.info('froxly - checher error', traceback.format_exc())