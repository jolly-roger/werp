import urllib.request
import urllib.parse
import traceback
import zmq
import json
import socket

from werp import nlog
from werp.common import sockets
from werp.common import timeouts

def run():
    try:
        ctx = zmq.Context()
        froxly_requester_worker_socket = ctx.socket(zmq.REP)
        froxly_requester_worker_socket.connect(sockets.froxly_requester_worker)
        rnd_user_agent_socket = ctx.socket(zmq.REQ)
        rnd_user_agent_socket.connect(sockets.rnd_user_agent)
        while True:
            req = json.loads(froxly_checker_req.recv_unicode())
            rnd_user_agent_socket.send_unicode('')
            rnd_user_agent = rnd_user_agent_socket.recv_unicode()
            try:
                s = socket.socket()
                s.settimeout(timeouts.froxly_requester)
                
                
                url_obj = urllib.parse.urlparse(task['url'])
                s.connect((task['proxy']['ip'], int(task['proxy']['port'])))
                req_str = 'GET ' + task['url'] + ' HTTP/1.1\r\nHost:' + url_obj.netloc + '\r\n\r\n'
                s.sendall(req_str.encode())
                res = s.recv(15).decode()
                s.close()
                if res == 'HTTP/1.1 200 OK' or res == 'HTTP/1.0 200 OK':
                    task['proxy']['http_status'] = 200
                    task['proxy']['http_status_reason'] = None
                else:
                    task['proxy']['http_status'] = -1
                    task['proxy']['http_status_reason'] = res
                    
                    
            except Exception as e:
                
                
                task['proxy']['http_status'] = -1
                task['proxy']['http_status_reason'] = str(e)
                
                
            froxly_requester_worker_socket.send_unicode(json.dumps(res))
    except:
        nlog.info('froxly - requester worker error', traceback.format_exc())