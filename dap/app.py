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

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(dap())
    cherrypy.log.screen = False
    return tree
    
