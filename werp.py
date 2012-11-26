from cherrypy.process import servers, plugins
from cherrypy import wsgiserver
import cherrypy
import os.path
import datetime


from errors import errors
from uatrains import uatrains, spider
from robots import robots
from picpuk import picpuk


WERP_ACCESS_LOG_FILE = '/home/www/werp_access.log'
werp_access_log_file = open(WERP_ACCESS_LOG_FILE, 'a')

def werp_access_log():
    headers = str(cherrypy.request.headers) if cherrypy.request.headers is not None else ''
    werp_access_log_file.write(cherrypy.request.base + ' "' + cherrypy.request.request_line + '" ' + \
        cherrypy.response.status + ' [' + \
        str(datetime.datetime.now()) + '] ' + '\n\n')
    werp_access_log_file.flush()

cherrypy.tools.werp_access_log = cherrypy.Tool('on_end_resource', werp_access_log)

def fake_wait_for_occupied_port(host, port): return
servers.wait_for_occupied_port = fake_wait_for_occupied_port

cherrypy.config.update({'tools.sessions.on': True,
    'tools.sessions.timeout': 30,
    'tools.werp_access_log.on': True,
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