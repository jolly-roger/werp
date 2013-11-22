import cherrypy
import json
import os.path
import urllib.request
import urllib.parse
import traceback

from werp import nlog
from . import layout
from . import engine
from . import sitemap


class ukrainianside(object):
    @cherrypy.expose
    def sitemap_xml(self):
        cherrypy.response.headers['Content-Type'] = "application/xml "

        return bytes(sitemap.getSitemap(), 'utf-8')
    
    @cherrypy.expose
    def index(self):
        return layout.getIndex()
    
    @cherrypy.expose
    def default(self, title=None, *args, **kwargs):
        articles = engine.article.getAll()
        if title is not None:
            return title
            try:
                nlog.info('Ukrainianside error', 'Yo!!!')
            except:
                nlog.info('Ukrainianside error', 'Yo!!!')
            
            alias = engine.article.getAliasByTitle(title)
            isexist = False
            if engine.article.isExist(title, articles): isexist = True
            else: isexist = False
            if isexist:
                return layout.getAticle(alias)
            else:    
                return layout.getHome()
        return layout.getHome()
    
    @cherrypy.expose
    def css(self):
        cherrypy.response.headers['Content-Type'] = "text/css"
        return layout.getCss()


def error_page_default(status, message, traceback, version):
    d = urllib.parse.urlencode({'status': status, 'message': message, 'traceback': traceback, 'version': version,
        'data': json.dumps({'subject': 'Ukrainianside error',
            'base': cherrypy.request.base, 'request_line': cherrypy.request.request_line,
            'headers': str(cherrypy.request.headers)})})
    d = d.encode('utf-8')
    req = urllib.request.Request('http://localhost:18404/sendmail')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8')
    res = urllib.request.urlopen(req, d)
    return res.read().decode()

def wsgi():
    tree = cherrypy._cptree.Tree()
    app = tree.mount(ukrainianside())
    app.config.update({'/': {'error_page.default': error_page_default},
        'tools.encode.on': True, 'tools.encode.encoding': 'utf-8'})
    cherrypy.log.screen = False
    return tree