import traceback
import cherrypy

from werp import nlog
from werp import orm

from . import layout

class dap(object):
    @cherrypy.expose
    def index(self, domain=None):
        return layout.getHome(domain)

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(dap())
    cherrypy.log.screen = False
    return tree
    
