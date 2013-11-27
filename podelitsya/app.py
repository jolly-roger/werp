import cherrypy
import json
import os.path
import urllib.request
import urllib.parse

from . import layout

class podelitsya(object):
    @cherrypy.expose
    def index(self):
        return 'podelitsya'
    
    @cherrypy.expose
    def social(self, u, t):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        qurl = urllib.parse.quote(u)
        return layout.getSocial(qurl, t)
    
    @cherrypy.expose
    def css(self):
        cherrypy.response.headers['Content-Type'] = "text/css"
        return layout.getCss()

def wsgi():
    tree = cherrypy._cptree.Tree()
    app = tree.mount(podelitsya())
    cherrypy.log.screen = False
    return tree
