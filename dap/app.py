import traceback
import cherrypy
import zmq
import json

from werp import nlog
from werp import orm
from werp.common import sockets

from . import layout

class dap(object):
    @cherrypy.expose
    def index(self, domain=None):
        if domain is not None and domain != '':
            ctx = zmq.Context()
            froxly_data_server_socket = ctx.socket(zmq.REQ)
            froxly_data_server_socket.connect(sockets.froxly_data_server)
            froxly_data_server_socket.send_unicode(json.dumps({'method': 'list_for_url', 'params':
                {'url': domain}}))
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
    
