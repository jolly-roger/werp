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

def run():
    try:
        ctx = zmq.Context()
        froxly_checker_req = ctx.socket(zmq.PULL)
        froxly_checker_req.connect(sockets.froxly_checker_req)
        ugently_data_server_socket = ctx.socket(zmq.REQ)
        ugently_data_server_socket.connect(sockets.ugently_data_server)
        froxly_checker_res = ctx.socket(zmq.PUSH)
        froxly_checker_res.connect(sockets.froxly_checker_res)
        while True:
            task = json.loads(froxly_checker_req.recv_unicode())
            ugently_data_server_socket.send_unicode('')
            rnd_user_agent = ugently_data_server_socket.recv_unicode()
            try:
                is_1_1 = False
                
                # HTTP 1.1
                s = socket.socket()
                s.settimeout(timeouts.froxly_checker)
                url_obj = urllib.parse.urlparse(task['url'])
                s.connect((task['proxy']['ip'], int(task['proxy']['port'])))
                req_str = 'GET ' + task['url'] + ' HTTP/1.1\r\nHost:' + url_obj.netloc + '\r\n\r\n'
                s.sendall(req_str.encode())
                res = s.recv(15).decode()
                s.close()
                if res == 'HTTP/1.1 200 OK':
                    is_1_1 = True
                    task['proxy']['http_status'] = 200
                    task['proxy']['http_status_reason'] = None
                    task['proxy']['protocol_version'] = '1.1'
                else:
                    task['proxy']['http_status'] = -1
                    task['proxy']['http_status_reason'] = res
                
                # HTTP 1.0
                if not is_1_1:
                    s = socket.socket()
                    s.settimeout(timeouts.froxly_checker)
                    url_obj = urllib.parse.urlparse(task['url'])
                    s.connect((task['proxy']['ip'], int(task['proxy']['port'])))
                    req_str = 'GET ' + task['url'] + ' HTTP/1.0\r\nHost:' + url_obj.netloc + '\r\n\r\n'
                    s.sendall(req_str.encode())
                    res = s.recv(15).decode()
                    s.close()
                    if res == 'HTTP/1.0 200 OK':
                        task['proxy']['http_status'] = 200
                        task['proxy']['http_status_reason'] = None
                        task['proxy']['protocol_version'] = '1.0'
                    else:
                        task['proxy']['http_status'] = -1
                        task['proxy']['http_status_reason'] = res
            except Exception as e:
                task['proxy']['http_status'] = -1
                task['proxy']['http_status_reason'] = str(e)
            froxly_checker_res.send_unicode(json.dumps(task))
    except:
        nlog.info('froxly - checher error', traceback.format_exc())