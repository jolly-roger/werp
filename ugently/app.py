import traceback
import cherrypy

from werp import nlog
from werp import orm

from . import layout

class ugently(object):
    @cherrypy.expose
    def index(self):
        l = 'No data'
        try:
            conn = orm.q_engine.connect()
            ses = orm.sescls(bind=conn)
            user_agents = ses.query(orm.UserAgent).all()
            l = layout.getHome(user_agents)
            ses.close()
            conn.close()
        except:
            nlog.info('ugently - error', traceback.format_exc())
        return l
    
    def login(self, name=None, pwd=None):
        l = layout.getLogin()
        return l

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(ugently())
    cherrypy.log.screen = False
    return tree
    
