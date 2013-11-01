import traceback
import cherrypy
import zmq
import json
import redis
import random

from werp import nlog
from werp import orm
from werp.common import sockets, red_keys
from werp.froxly.data_server import common as data_server_common

from . import layout

class dap(object):
    @cherrypy.expose
    def index(self, domain=None):
        if domain is not None and domain != '':
            red = redis.StrictRedis(unix_socket_path=sockets.redis)
            base_proxies = red.smembers(red_keys.froxly_base_check_free_proxy)
            proxies_key = red_keys.froxly_url_free_proxy_prefix + domain
            to_check_key = red_keys.froxly_url_free_proxy_to_check_prefix + domain
            if red.exists(proxies_key):
                red.delete(proxies_key)
            if red.exists(to_check_key):
                red.delete(to_check_key)
            if len(base_proxies) >= 10:
                while red.scard(to_check_key) < 10:
                    p = random.choice(base_proxies)
                    proxy = json.loads(p.decode('utf-8'))
                    sproxy = data_server_common.jproxy2sproxy(proxy)
                    red.sadd(to_check_key, sproxy)
            ctx = zmq.Context()
            froxly_data_server_socket = ctx.socket(zmq.REQ)
            froxly_data_server_socket.connect(sockets.froxly_data_server)
            froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
                {'url': domain, 'worker_pool': 3, 'to_check_key': to_check_key}}))
            froxly_data_server_socket.recv_unicode()
        return layout.getHome(domain)
    
    @cherrypy.expose
    def get_10_checked(self, domain=None):
        rnd_10_proxies = []
        if domain is not None and domain != '':
            ctx = zmq.Context()
            froxly_data_server_socket = ctx.socket(zmq.REQ)
            froxly_data_server_socket.connect(sockets.froxly_data_server)
            for i in range(10):
                rnd_proxy_req = {'method': 'rnd_for_url', 'params': {'url': domain}}
                froxly_data_server_socket.send_unicode(json.dumps(rnd_proxy_req))
                rnd_10_proxies.append(json.loads(froxly_data_server_socket.recv_unicode())['result'])
        return json.dumps(rnd_10_proxies)

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(dap())
    cherrypy.log.screen = False
    return tree
    
