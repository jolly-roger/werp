import traceback
import cherrypy

from werp import nlog
from werp import orm

from . import layout

class dap(object):
    @cherrypy.expose
    def index(self):
        l = 'No data'
        #try:
        #    conn = orm.q_engine.connect()
        #    ses = orm.sescls(bind=conn)
        #    user_agents = ses.query(orm.UserAgent).all()
        #    l = layout.getHome(user_agents)
        #    ses.close()
        #    conn.close()
        #except:
        #    nlog.info('dap - error', traceback.format_exc())
        return l

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(dap())
    cherrypy.log.screen = False
    return tree
    
