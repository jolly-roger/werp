import traceback
import cherrypy
import zmq
import json
import redis
import random
import uuid

from werp import nlog
from werp import orm
from werp.common import sockets, red_keys
from werp.froxly.data_server import common as data_server_common

from . import layout

red = redis.StrictRedis(unix_socket_path=sockets.redis)

class dap(object):
    @cherrypy.expose
    def index(self):
        lng = get_lng()
        ses_key = _create_ses()
        proxies = []
        jproxies = '['
        base_proxies = red.smembers(red_keys.froxly_base_check_free_proxy)
        if len(base_proxies) >= 10:
            ps = random.sample(base_proxies, 10)
            for p in ps:
                proxy = json.loads(p.decode('utf-8'))
                proxies.append(proxy)
                jproxies += data_server_common.jproxy2sproxy(proxy) + ','
        if jproxies.endswith(','):
            jproxies = jproxies[:-1]
        jproxies += ']'
        return layout.getHome(ses_key, proxies, jproxies, lng)
    
    @cherrypy.expose
    def check_10(self, ses_key=None, domain=None, jproxies=None):
        if ses_key is not None and ses_key != '' and red.exists(red_keys.dap_ses_key_prefix + ses_key):
            rnd_base_proxies = []
            if domain is not None and domain != '' and jproxies is not None and jproxies != '':
                domain = 'http://' + domain
                proxies = json.loads(jproxies)
                if red.exists(red_keys.froxly_url_free_proxy_finish_prefix + domain):
                    red.delete(red_keys.froxly_url_free_proxy_finish_prefix + domain)
                if len(proxies) >= 10 and not red.exists(red_keys.froxly_url_free_proxy_to_check_prefix + domain):
                    for proxy in proxies:
                        sproxy = data_server_common.jproxy2sproxy(proxy)
                        red.sadd(red_keys.froxly_url_free_proxy_to_check_prefix + domain, sproxy)
                ctx = zmq.Context()
                froxly_data_server_socket = ctx.socket(zmq.REQ)
                froxly_data_server_socket.connect(sockets.froxly_data_server)
                froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
                    {'url': domain, 'worker_pool': 10,
                        'to_check_key': red_keys.froxly_url_free_proxy_to_check_prefix + domain}}))
                froxly_data_server_socket.recv_unicode()
            return ''
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/'
    
    @cherrypy.expose
    def get_10_checked(self, ses_key=None, domain=None):
        if ses_key is not None and ses_key != '' and red.exists(red_keys.dap_ses_key_prefix + ses_key):
            rnd_10_proxies = []
            if domain is not None and domain != '':
                domain = 'http://' + domain
                if red.exists(red_keys.froxly_url_free_proxy_prefix + domain):
                    ps = red.smembers(red_keys.froxly_url_free_proxy_prefix + domain)
                    for p in ps:
                        proxy = json.loads(p.decode('utf-8'))
                        rnd_10_proxies.append(proxy)
            return json.dumps(rnd_10_proxies)
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/'
    
    @cherrypy.expose
    def is_check_finished(self, ses_key=None, domain=None):
        if ses_key is not None and ses_key != '' and red.exists(red_keys.dap_ses_key_prefix + ses_key):
            if domain is not None and domain != '':
                domain = 'http://' + domain
                if red.exists(red_keys.froxly_url_free_proxy_finish_prefix + domain):
                    if red.exists(red_keys.froxly_url_free_proxy_prefix + domain):
                        red.delete(red_keys.froxly_url_free_proxy_prefix + domain)
                    if red.exists(red_keys.froxly_url_free_proxy_to_check_prefix + domain):
                        red.delete(red_keys.froxly_url_free_proxy_to_check_prefix + domain)
                    return 'true'
            return 'false'
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/'
    
    @cherrypy.expose
    def css(self):
        cherrypy.response.headers['Content-Type'] = "text/css"
        return layout.getCss()
    
    @cherrypy.expose
    def js(self):
        lng = get_lng()
        cherrypy.response.headers['Content-Type'] = "text/javascript"
        return layout.getJS(lng)

def get_lng():
    domain = cherrypy.request.base.lower().replace('http://', '')
    if domain.startswith('ru.'):
        return 'RU'
    return 'EN'
    
def _create_ses():
    ses_key = str(uuid.uuid4())
    red.set(red_keys.dap_ses_key_prefix + ses_key, '', ex=900)
    return ses_key

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(dap())
    cherrypy.log.screen = False
    return tree
    
