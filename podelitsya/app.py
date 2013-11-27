import cherrypy
import json
import os.path
import urllib.request
import urllib.parse
import traceback

from werp import nlog
from . import layout

class podelitsya(object):
    @cherrypy.expose
    def index(self):
        return 'podelitsya'
    
    @cherrypy.expose
    def social(self, u, t, l=0):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        try:
            qurl = urllib.parse.quote(u)
            display_label = True if int(l) > 0 else False
            return layout.getSocial(qurl, t, display_label)
        except:
            nlog.info('podelitsya error', traceback.format_exc())
            return ''
    
    @cherrypy.expose
    def css(self):
        cherrypy.response.headers['Content-Type'] = "text/css"
        return layout.getCss()

def wsgi():
    tree = cherrypy._cptree.Tree()
    app = tree.mount(podelitsya())
    cherrypy.log.screen = False
    return tree
