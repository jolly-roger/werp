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
    def index(self):
        return layout.getHome()
    
    @cherrypy.expose
    def check_10(self, domain=None):
        rnd_base_proxies = []
        if domain is not None and domain != '':
            red = redis.StrictRedis(unix_socket_path=sockets.redis)
            base_proxies = red.smembers(red_keys.froxly_base_check_free_proxy)
            to_check_key = red_keys.froxly_url_free_proxy_to_check_prefix + domain
            if len(base_proxies) >= 10 and not red.exists(to_check_key):
                ps = random.sample(base_proxies, 10)
                for p in ps:
                    proxy = json.loads(p.decode('utf-8'))
                    rnd_base_proxies.append(proxy)
                    sproxy = data_server_common.jproxy2sproxy(proxy)
                    red.sadd(to_check_key, sproxy)
                ctx = zmq.Context()
                froxly_data_server_socket = ctx.socket(zmq.REQ)
                froxly_data_server_socket.connect(sockets.froxly_data_server)
                froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
                    {'url': domain, 'worker_pool': 10, 'to_check_key': to_check_key}}))
                froxly_data_server_socket.recv_unicode()
            elif red.exists(to_check_key):
                to_check = red.smembers(to_check_key)
                for p in to_check:
                    proxy = json.loads(p.decode('utf-8'))
                    rnd_base_proxies.append(proxy)
        return json.dumps(rnd_base_proxies)
    
    @cherrypy.expose
    def get_10_checked(self, domain=None):
        rnd_10_proxies = []
        if domain is not None and domain != '':
            red = redis.StrictRedis(unix_socket_path=sockets.redis)
            proxies_key = red_keys.froxly_url_free_proxy_prefix + domain
            if red.exists(proxies_key):
                ps = red.smembers(proxies_key)
                for p in ps:
                    proxy = json.loads(p.decode('utf-8'))
                    rnd_10_proxies.append(proxy)
        return json.dumps(rnd_10_proxies)
    
    @cherrypy.expose
    def is_check_finished(self, domain):
        if domain is not None and domain != '':
            red = redis.StrictRedis(unix_socket_path=sockets.redis)
            finish_key = red_keys.froxly_url_free_proxy_finish_prefix + domain
            if red.exists(finish_key):
                red.delete(finish_key)
                proxies_key = red_keys.froxly_url_free_proxy_prefix + domain
                to_check_key = red_keys.froxly_url_free_proxy_to_check_prefix + domain
                if red.exists(proxies_key):
                    red.delete(proxies_key)
                if red.exists(to_check_key):
                    red.delete(to_check_key)
                return 'true'
        return 'false'

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(dap())
    cherrypy.log.screen = False
    return tree
    
