import cherrypy
import json
import os.path
import traceback
    
    
from werp import orm, nlog, error_log
from werp.uatrains import search

from .common import etype
from .layout import layout
from . engine import lng as lngs
from . import sitemap


class uatrains(object):
    @cherrypy.expose
    def index(self, eid=None):
        lng = get_lng()
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        ts = []
        pc = 5
        try:
            q = None
            if lng == lngs.UA:
                q = ses.query(orm.uatrains.E).\
                    filter(orm.and_(orm.uatrains.E.etype == etype.train, orm.uatrains.E.ref_id == None)).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            if lng == lngs.RU:
                q = ses.query(orm.uatrains.E).\
                    filter(orm.and_(orm.uatrains.E.etype == etype.train, orm.uatrains.E.ref_id == None)).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ru_title)
            if lng == lngs.EN:
                q = ses.query(orm.uatrains.E).\
                    filter(orm.and_(orm.uatrains.E.etype == etype.train, orm.uatrains.E.ref_id == None)).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.en_title)
            ts = q.limit(pc).all()
        except Exception:
            nlog.info('Uatrains error', 'Can\'t find trains\n' + traceback.format_exc())
        ss = []
        try:
            q = None
            if lng == lngs.UA:
                q = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == etype.station).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            if lng == lngs.RU:
                q = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == etype.station).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ru_title)
            if lng == lngs.EN:
                q = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == etype.station).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.en_title)
            ss = q.limit(pc).all()
        except Exception:
            nlog.info('Uatrains error', 'Can\'t find stations\n' + traceback.format_exc())
        news = []
        try:
            news = ses.query(orm.uatrains.New).filter(orm.uatrains.New.lng == lng).\
                order_by(orm.uatrains.New.date.desc()).limit(3).all()
        except:
            nlog.info('Uatrains error', 'Can\'t find news\n' + traceback.format_exc())
        ses.close()
        conn.close()
        return layout.getHome(ts, ss, news, lng)
    @cherrypy.expose
    def default(self, eid=None, *a, **kw):
        lng = get_lng()
        l = ''
        ref_id = None
        if eid is not None:
            prepared_eid = None
            try:
                prepared_eid = int(float(eid))
            except:
                nlog.info('Uatrains error', 'Can\'t parse eid = ' + str(prepared_eid) + '\n' +\
                    traceback.format_exc())
            if prepared_eid is not None:
                conn = orm.q_engine.connect()
                ses = orm.sescls(bind=conn)
                e = None
                try:
                    e = ses.query(orm.uatrains.E).filter(orm.uatrains.E.id == prepared_eid).one()
                    if e.ref_id is not None:
                        ref_id = e.ref_id
                    else:
                        e.vc = e.vc + 1
                        ses.commit()
                except:
                    nlog.info('Uatrains error', 'Can\'t find entity by eid = ' + str(prepared_eid) + '\n' +\
                        traceback.format_exc())
                if e is not None and ref_id is None:
                    if e.etype == etype.train:
                        try:
                            t = ses.query(orm.uatrains.E).\
                                options(orm.joinedload_all(orm.uatrains.E.t_ss, orm.uatrains.TrainStation.s)).\
                                filter(orm.uatrains.E.id == prepared_eid).one()
                            l = layout.getTrain(t, t.t_ss, lng)
                        except:
                            nlog.info('Uatrains error', 'Can\'t find train by id = ' + str(prepared_eid) + '\n' +\
                                traceback.format_exc())
                    elif e.etype == etype.ptrain:
                        try:
                            t = ses.query(orm.uatrains.E).\
                                options(orm.joinedload_all(orm.uatrains.E.t_ss, orm.uatrains.TrainStation.s)).\
                                filter(orm.uatrains.E.id == prepared_eid).one()
                            l = layout.getPTrain(t, t.t_ss, lng)
                        except:
                            nlog.info('Uatrains error', 'Can\'t find ptrain by id = ' + str(prepared_eid) + '\n' +\
                                traceback.format_exc())
                    elif e.etype == etype.station:
                        try:
                            s = ses.query(orm.uatrains.E).\
                                options(orm.joinedload_all(orm.uatrains.E.s_ts, orm.uatrains.TrainStation.t)).\
                                filter(orm.uatrains.E.id == prepared_eid).one()
                            l = layout.getStation(s, s.s_ts, lng)
                        except:
                            nlog.info('Uatrains error', 'Can\'t find station by id = ' + str(prepared_eid) + '\n' +\
                                traceback.format_exc())
                ses.close()
                conn.close()
        else:
            l = self.index(eid)
        if l == '':
            cherrypy.response.status = 301
            if ref_id is not None:
                cherrypy.response.headers['Location'] = '/' + str(ref_id)
            else:
                cherrypy.response.headers['Location'] = '/'
        return l
    @cherrypy.expose
    def getstation(self, sid=-1):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/s/' + str(sid)
        return ''
    @cherrypy.expose
    def station(self, sid=-1):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/s/' + str(sid)
        return ''
    @cherrypy.expose
    def s(self, sid):
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        id = None
        try:
            ss = ses.query(orm.uatrains.E).filter(orm.and_(orm.uatrains.E.oid == int(sid),
                orm.uatrains.E.etype == etype.station)).all()
            s = ss[0]
            for station in ss:
                if s.id < station.id:
                    s = station
            id = s.id
        except:
            nlog.info('Uatrains error', 'Can\'t find station by sid = ' + str(sid) + '\n' +\
                traceback.format_exc())
        ses.close()
        conn.close()
        cherrypy.response.status = 301
        if id is not None:
            cherrypy.response.headers['Location'] = '/' + str(id)
        else:
            cherrypy.response.headers['Location'] = '/'
        return ''
    @cherrypy.expose
    def gettrain(self, tid=-1):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/t/' + str(tid)
        return ''
    @cherrypy.expose
    def train(self, tid=-1):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/t/' + str(tid)
        return ''
    @cherrypy.expose
    def t(self, tid):
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        id = None
        try:
            ts = ses.query(orm.uatrains.E).filter(orm.and_(orm.uatrains.E.oid == int(tid),
                orm.uatrains.E.etype == etype.train)).all()
            t = ts[0]
            for train in ts:
                if t.id < train.id and t.ref_id is None:
                    t = train
            id = t.id
        except:
            nlog.info('Uatrains error', 'Can\'t find train by tid = ' + str(tid) + '\n' +\
                traceback.format_exc())
        ses.close()
        conn.close()
        cherrypy.response.status = 301
        if id is not None:
            cherrypy.response.headers['Location'] = '/' + str(id)
        else:
            cherrypy.response.headers['Location'] = '/'
        return ''
    @cherrypy.expose
    def stations(self, phrase='', pn=0):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/ss?ph=%s&pn=%s' % (phrase, pn)
        return ''
    @cherrypy.expose
    def ss(self, ph='', pn=0):
        lng = get_lng()
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        pn = int(pn)
        pc = 9
        ss = []
        has_next_p = False
        try:
            q = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == etype.station).\
                filter(orm.or_(orm.uatrains.E.ua_title.ilike('%' + ph.lower() + '%'),
                orm.uatrains.E.ru_title.ilike('%' + ph.lower() + '%'),
                orm.uatrains.E.en_title.ilike('%' + ph.lower() + '%'))).\
                order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            ss = q.limit(pc).offset(pn * pc).all()
            next_p_ss = q.limit(pc).offset((pn + 1) * pc).all()
            if len(next_p_ss) > 0:
                has_next_p = True
        except Exception:
            nlog.info('Uatrains error', 'Can\'t find stations\n' + traceback.format_exc())
        ses.close()
        conn.close()
        return layout.getStations(ss, ph, pn, has_next_p, lng)
    @cherrypy.expose
    def trains(self, phrase='', pn=0):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/ts?ph=%s&pn=%s' % (phrase, pn)
        return ''
    @cherrypy.expose
    def ts(self, ph='', pn=0):
        lng = get_lng()
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        pn = int(pn)
        pc = 9
        ts = []
        has_next_p = False
        try:
            q = None
            if lng == lngs.UA:
                q = ses.query(orm.uatrains.E).\
                    filter(orm.and_(orm.or_(orm.uatrains.E.etype == etype.train, orm.uatrains.E.etype == etype.etrain,
                        orm.uatrains.E.etype == etype.ptrain),
                        orm.uatrains.E.ua_graph.ilike('%' + ph.lower().replace(' ', '%') + '%'),
                        orm.uatrains.E.ua_title.ilike('%' + ph.lower() + '%'), orm.uatrains.E.ref_id == None)).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            if lng == lngs.RU:
                q = ses.query(orm.uatrains.E).\
                    filter(orm.and_(orm.or_(orm.uatrains.E.etype == etype.train, orm.uatrains.E.etype == etype.etrain,
                        orm.uatrains.E.etype == etype.ptrain),
                        orm.uatrains.E.ru_graph.ilike('%' + ph.lower().replace(' ', '%') + '%'),
                        orm.uatrains.E.ru_title.ilike('%' + ph.lower() + '%'), orm.uatrains.E.ref_id == None)).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ru_title)
            if lng == lngs.EN:
                q = ses.query(orm.uatrains.E).\
                    filter(orm.and_(orm.or_(orm.uatrains.E.etype == etype.train, orm.uatrains.E.etype == etype.etrain,
                        orm.uatrains.E.etype == etype.ptrain),
                        orm.uatrains.E.en_graph.ilike('%' + ph.lower().replace(' ', '%') + '%'),
                        orm.uatrains.E.en_title.ilike('%' + ph.lower() + '%'), orm.uatrains.E.ref_id == None)).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.en_title)
            ts = q.limit(pc).offset(pn * pc).all()
            next_p_ts = q.limit(pc).offset((pn + 1) * pc).all()
            if len(next_p_ts) > 0:
                has_next_p = True
        except Exception:
            nlog.info('Uatrains error', 'Can\'t find trains\n' + traceback.format_exc())
        ses.close()
        conn.close()
        return layout.getTrains(ts, ph, pn, has_next_p, lng)
    @cherrypy.expose
    def es(self, srcht=0, ph='', fs='', ts='', pn=0, pc=9):
        lng = get_lng()
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        pn = int(pn)
        pc = int(pc)
        es = []
        has_next_p = False
        if int(srcht) == 0:
            es, has_next_p = search.from_to(ses, fs, ts, pc, pn)
        elif int(srcht) == 1:
            prepared_ph = ph.replace(' ', '%').replace('-', '%')
            es, has_next_p = search.full(ses, ph, pc, pn)
        ses.close()
        conn.close()
        return layout.getEs(es, srcht, ph, fs, ts, pn, has_next_p, lng)
    @cherrypy.expose
    def news(self):
        lng = get_lng()
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        news = []
        try:
            news = ses.query(orm.uatrains.New).filter(orm.uatrains.New.lng == lng).\
                order_by(orm.uatrains.New.date.desc()).all()
        except:
            nlog.info('Uatrains error', 'Can\'t find news\n' + traceback.format_exc())
        ses.close()
        conn.close()
        return layout.getNews(news, lng)
    @cherrypy.expose
    def css(self):
        cherrypy.response.headers['Content-Type'] = "text/css"
        return layout.getCss()
    @cherrypy.expose
    def sitemap_xml(self):
        cherrypy.response.headers['Content-Type'] = "application/xml "
        lng = get_lng()
        return bytes(sitemap.getSitemap(lng), 'utf-8')
    @cherrypy.expose
    def trainsitemap_xml(self):
        cherrypy.response.headers['Content-Type'] = "application/xml "
        lng = get_lng()
        return bytes(sitemap.getTrainSitemap(lng), 'utf-8')
    @cherrypy.expose
    def stationsitemap_xml(self):
        cherrypy.response.headers['Content-Type'] = "application/xml "
        lng = get_lng()
        return bytes(sitemap.getStationSitemap(lng), 'utf-8')
    @cherrypy.expose
    def ptrainsitemap_xml(self):
        cherrypy.response.headers['Content-Type'] = "application/xml "
        lng = get_lng()
        return bytes(sitemap.getPTrainSitemap(lng), 'utf-8')

def get_lng():
    domain = cherrypy.request.base.lower().replace('http://', '')
    if domain.startswith('ru.'):
        return lngs.RU
    elif domain.startswith('en.'):
        return lngs.EN
    return lngs.UA

def wsgi():
    tree = cherrypy._cptree.Tree()
    tree.mount(uatrains())
    cherrypy.log.screen = False
    return tree