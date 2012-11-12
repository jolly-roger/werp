from cherrypy.process import servers, plugins
from cherrypy import wsgiserver
import cherrypy
import os.path


from errors import errors
from uatrains import uatrains, spider
from robots import robots
from picpuk import picpuk


def fake_wait_for_occupied_port(host, port): return
servers.wait_for_occupied_port = fake_wait_for_occupied_port

cherrypy.config.update({'tools.sessions.on': True,
    'tools.sessions.timeout': 30,
    'server.thread_pool': 111,
    'server.socket_queue_size': 33,
    'log.access_file': '/home/www/access.log',
    'log.error_file': '/home/www/errors.log'})

wsgis = []
wsgis.append(uatrains.wsgi())
wsgis.append(spider.wsgi())
wsgis.append(errors.wsgi())
wsgis.append(robots.wsgi())
wsgis.append(picpuk.wsgi())

cherrypy.server.unsubscribe()

for wsgi in wsgis:
    s = cherrypy.wsgiserver.CherryPyWSGIServer(wsgi.bind_address, wsgi)
    sa = servers.ServerAdapter(cherrypy.engine, s)
    sa.subscribe()

plugins.Daemonizer(cherrypy.engine).subscribe()

cherrypy.engine.start()