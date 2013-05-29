import urllib.request
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
        froxly_requester_server_socket = ctx.socket(zmq.REP)
        froxly_requester_server_socket.connect(sockets.froxly_requester_server)
        rnd_user_agent_socket = ctx.socket(zmq.REQ)
        rnd_user_agent_socket.connect(sockets.rnd_user_agent)
        while True:
            req_msg = froxly_requester_server_socket.recv_unicode()
            
            nlog.info('froxly - requester worker info', req_msg)
            
            res = {'result': {'data': None, 'http_status': None, 'http_status_reason': None, 'url': None}}
            try:
                s = socket.socket()
                s.settimeout(timeouts.froxly_requester)
                req = json.loads(req_msg)
                res['result']['url'] = req['params']['url']
                url_obj = urllib.parse.urlparse(req['params']['url'])
                rnd_user_agent_socket.send_unicode('')
                rnd_user_agent = rnd_user_agent_socket.recv_unicode()
                s.connect((req['params']['proxy']['ip'], int(req['params']['proxy']['port'])))
                remote_req_str = 'GET ' + req['params']['url'] + ' HTTP/1.1\r\nHost:' + url_obj.netloc + '\r\n\r\n'
                s.sendall(remote_req_str.encode())
                remote_charset = 'utf-8'
                if 'charset' in req['params'] and req['params']['charset'] is not None:
                    remote_charset = req['params']['charset']
                remote_res = s.recv(15).decode(remote_charset)
                if remote_res == 'HTTP/1.1 200 OK' or remote_res == 'HTTP/1.0 200 OK':
                    buf = s.recv(1024)
                    while buf:
                        remote_res += buf.decode(remote_charset)
                        buf = s.recv(1024)
                    start_body = remote_res.find('\r\n\r\n')
                    res['result']['data'] = remote_res[start_body + 4:]
                    res['result']['http_status'] = 200
                    res['result']['http_status_reason'] = None
                else:
                    res['result']['http_status'] = -1
                    res['result']['http_status_reason'] = remote_res
                s.close()
            except Exception as e:
                res['result']['http_status'] = -11
                res['result']['http_status_reason'] = str(e)
            froxly_requester_server_socket.send_unicode(json.dumps(res))
    except:
        nlog.info('froxly - requester worker error', traceback.format_exc())