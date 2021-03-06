import traceback
import cherrypy

from . import layout
from . import check
from .engine import common

class dap(object):
    check = check.check()
    
    @cherrypy.expose
    def index(self):
        lng = common.get_lng()
        return layout.getHome(lng)
    
    @cherrypy.expose
    def css(self):
        cherrypy.response.headers['Content-Type'] = "text/css"
        return layout.getCss()
    
    @cherrypy.expose
    def js(self, page=None):
        lng = common.get_lng()
        cherrypy.response.headers['Content-Type'] = "text/javascript"
        return layout.getJS(page, lng)

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(dap())
    cherrypy.log.screen = False
    return tree
    
