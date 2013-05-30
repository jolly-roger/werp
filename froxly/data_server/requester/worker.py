import urllib.request
import traceback
import zmq
import json
import socket

from werp import nlog
from werp.common import sockets
from werp.common import timeouts
from werp.froxly.data_server import common as data_server_common

def run():
    try:
        ctx = zmq.Context()
        
        froxly_requester_worker_socket = ctx.socket(zmq.REP)
        froxly_requester_worker_socket.connect(sockets.froxly_requester_worker)
        
        ugently_data_server_socket = ctx.socket(zmq.REQ)
        ugently_data_server_socket.connect(sockets.ugently_data_server)
        
        froxly_data_server_socket = ctx.socket(zmq.REQ)
        froxly_data_server_socket.connect(sockets.froxly_data_server)
        
        while True:
            req_msg = froxly_requester_worker_socket.recv_unicode()
            req_url = None
            res = {'result': {'data': None, 'http_status': None, 'http_status_reason': None}}
            try:
                s = socket.socket()
                s.settimeout(timeouts.froxly_requester)
                req = json.loads(req_msg)
                req_url = req['params']['url']
                url_obj = urllib.parse.urlparse(req['params']['url'])
                ugently_data_server_socket.send_unicode('')
                rnd_user_agent = ugently_data_server_socket.recv_unicode()
                rnd_proxy_req = {'method': 'rnd_for_url', 'params': None}
                if url_obj.netloc is not None and url_obj.netloc != '':
                    rnd_proxy_req['params'] = {'url': url_obj.scheme + '://' + url_obj.netloc}                
                froxly_data_server_socket.send_unicode(json.dumps(rnd_proxy_req))
                rnd_proxy = json.loads(froxly_data_server_socket.recv_unicode())['result']
                s.connect((rnd_proxy['ip'], int(rnd_proxy['port'])))
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
                if req_url is not None:
                    sproxy = data_server_common.jproxy2sproxy(rnd_proxy)
                    deactivate_proxy_req = {'method': 'deactivate_for_url', 'params':
                        {'url': req_url, 'proxy': sproxy, 'reason': res['result']['http_status_reason']}}
                    froxly_data_server_socket.send_unicode(json.dumps(deactivate_proxy_req))
                    froxly_data_server_socket.recv_unicode()
            froxly_requester_worker_socket.send_unicode(json.dumps(res))
    except:
        nlog.info('froxly - requester worker fatal', traceback.format_exc())