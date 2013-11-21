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
from .engine import session
from .engine import common

red = redis.StrictRedis(unix_socket_path=sockets.redis)

class check(object):
    @cherrypy.expose
    def default(self, domain=None):
        lng = common.get_lng()
        ses_key = session.create()
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
        if ses_key is not None and ses_key != '' and session.exists(ses_key):
            rnd_base_proxies = []
            if domain is not None and domain != '' and jproxies is not None and jproxies != '':
                domain_value = 'http://' + domain
                proxies = json.loads(jproxies)
                if red.exists(red_keys.froxly_url_free_proxy_finish_prefix + domain_value):
                    red.delete(red_keys.froxly_url_free_proxy_finish_prefix + domain_value)
                if len(proxies) >= 10 and not red.exists(red_keys.froxly_url_free_proxy_to_check_prefix + domain_value):
                    for proxy in proxies:
                        sproxy = data_server_common.jproxy2sproxy(proxy)
                        red.sadd(red_keys.froxly_url_free_proxy_to_check_prefix + domain_value, sproxy)
                ctx = zmq.Context()
                froxly_data_server_socket = ctx.socket(zmq.REQ)
                froxly_data_server_socket.connect(sockets.froxly_data_server)
                froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
                    {'url': domain_value, 'worker_pool': 10,
                        'to_check_key': red_keys.froxly_url_free_proxy_to_check_prefix + domain_value}}))
                froxly_data_server_socket.recv_unicode()
        return layout.getCheck(domain, ses_key, proxies, jproxies, lng)
    
    @cherrypy.expose
    def get_checked(self, ses_key=None, domain=None):
        if ses_key is not None and ses_key != '' and session.exists(ses_key):
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
    def is_finished(self, ses_key=None, domain=None):
        if ses_key is not None and ses_key != '' and session.exists(ses_key):
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