from cherrypy.process import servers, plugins
from cherrypy import wsgiserver
import cherrypy
import os.path
import datetime
import logging


from errors import errors
from uatrains import uatrains, spider
from robots import robots
from picpuk import picpuk


logging.basicConfig(filename='werp_error.log',level=logging.DEBUG)


WERP_ACCESS_LOG_FILE = '/home/www/werp_access.log'
werp_access_log_file = open(WERP_ACCESS_LOG_FILE, 'a')

def werp_access_log():
    headers = str(cherrypy.request.headers) if cherrypy.request.headers is not None else '[No headers]'
    domain = str(cherrypy.request.base) if cherrypy.request.base is not None else '[No domain]'
    request_line = str(cherrypy.request.request_line) if cherrypy.request.request_line is not None else '[No request line]'
    status = str(cherrypy.response.status) if cherrypy.response.status is not None else '[No status]'
    werp_access_log_file.write(domain + ' "' + request_line + '" ' + status + ' [' + \
        str(datetime.datetime.now()) + '] ' + headers + '\n\n')
    werp_access_log_file.flush()

cherrypy.tools.werp_access_log = cherrypy.Tool('on_end_resource', werp_access_log)

def fake_wait_for_occupied_port(host, port): return
servers.wait_for_occupied_port = fake_wait_for_occupied_port

cherrypy.config.update({
    'tools.sessions.on': False,
    'tools.encode.on': True,
    'tools.encode.encoding': 'utf-8',
    'tools.encode.text_only': False,
    'tools.gzip.on': True,
    'tools.werp_access_log.on': True,
    'server.thread_pool': 333,
    'server.socket_queue_size': 111,
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