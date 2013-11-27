import cherrypy
import json
import os.path
import urllib.request
import urllib.parse

from werp import error_log
from . import layout

class podelitsya(object):
    @cherrypy.expose
    def index(self):
        return 'podelitsya'
    
    @cherrypy.expose
    def social(self, url, title):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        
        
        error_log.info(str(url))
        
        
        #quoted_url = url.encode('latin-1').decode('utf8').strip()
        return layout.getSocial(url, title)
    
    @cherrypy.expose
    def css(self):
        cherrypy.response.headers['Content-Type'] = "text/css"
        return layout.getCss()

def wsgi():
    tree = cherrypy._cptree.Tree()
    app = tree.mount(podelitsya())
    cherrypy.log.screen = False
    return tree
