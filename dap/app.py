import traceback
import cherrypy

from . import layout
#from . import check

class dap(object):
    #check = check.check()
    
    @cherrypy.expose
    def index(self):
        lng = get_lng()
        return layout.getHome(lng)
    
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

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(dap())
    cherrypy.log.screen = False
    return tree
    
