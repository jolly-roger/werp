from cherrypy.process import servers
from cherrypy import wsgiserver
import cherrypy
import os.path


from uatrains import uatrains, spider


def fake_wait_for_occupied_port(host, port): return
servers.wait_for_occupied_port = fake_wait_for_occupied_port

wsgis = []
wsgis.append(uatrains.wsgi())
wsgis.append(spider.wsgi())

cherrypy.server.unsubscribe()

for wsgi in wsgis:
    s = cherrypy.wsgiserver.CherryPyWSGIServer(wsgi.bind_address, wsgi)
    sa = servers.ServerAdapter(cherrypy.engine, s)
    sa.subscribe()

cherrypy.engine.start()