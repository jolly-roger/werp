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
    def social(self, url, title):
        quoted_url = url.encode('latin-1').decode('utf8').strip()
        return layout.getSocial(quoted_url, title)

def wsgi():
    tree = cherrypy._cptree.Tree()
    app = tree.mount(podelitsya())
    cherrypy.log.screen = False
    return tree
