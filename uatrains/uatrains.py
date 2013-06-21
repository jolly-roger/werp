import cherrypy
import json
import os.path
import traceback
import logging
    
    
from werp import orm
from .common import etype
from .layout import layout
from . import notifier
from . engine import lng as lngs
from . import sitemap


logger = logging.getLogger('werp_error.uatrains')


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
                q = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == etype.train).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            if lng == lngs.RU:
                q = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == etype.train).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ru_title)
            if lng == lngs.EN:
                q = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == etype.train).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.en_title)
            ts = q.limit(pc).all()
        except Exception:
            notifier.notify('Uatrains error', 'Can\'t find trains\n' + traceback.format_exc())
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
            notifier.notify('Uatrains error', 'Can\'t find stations\n' + traceback.format_exc())
        news = []
        try:
            news = ses.query(orm.uatrains.New).filter(orm.uatrains.New.lng == lng).\
                order_by(orm.uatrains.New.date.desc()).limit(3).all()
        except:
            notifier.notify('Uatrains error', 'Can\'t find news\n' + traceback.format_exc())
        ses.close()
        conn.close()
        return layout.getHome(ts, ss, news, lng)
    @cherrypy.expose
    def default(self, eid=None):
        lng = get_lng()
        l = ''
        ref_id = None
        if eid is not None:
            prepared_eid = None
            try:
                prepared_eid = int(float(eid))
            except:
                notifier.notify('Uatrains error', 'Can\'t parse eid = ' + str(prepared_eid) + '\n' +\
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
                    notifier.notify('Uatrains error', 'Can\'t find entity by eid = ' + str(prepared_eid) + '\n' +\
                        traceback.format_exc())
                if e is not None and ref_id is None:
                    if e.etype == etype.train:
                        try:
                            t = ses.query(orm.uatrains.E).\
                                options(orm.joinedload_all(orm.uatrains.E.t_ss, orm.uatrains.TrainStation.s)).\
                                filter(orm.uatrains.E.id == prepared_eid).one()
                            l = layout.getTrain(t, t.t_ss, lng)
                        except:
                            notifier.notify('Uatrains error', 'Can\'t find train by id = ' + str(prepared_eid) + '\n' +\
                                traceback.format_exc())
                    elif e.etype == etype.ptrain:
                        try:
                            t = ses.query(orm.uatrains.E).\
                                options(orm.joinedload_all(orm.uatrains.E.t_ss, orm.uatrains.TrainStation.s)).\
                                filter(orm.uatrains.E.id == prepared_eid).one()
                            l = layout.getPTrain(t, t.t_ss, lng)
                        except:
                            notifier.notify('Uatrains error', 'Can\'t find ptrain by id = ' + str(prepared_eid) + '\n' +\
                                traceback.format_exc())
                    elif e.etype == etype.station:
                        try:
                            s = ses.query(orm.uatrains.E).\
                                options(orm.joinedload_all(orm.uatrains.E.s_ts, orm.uatrains.TrainStation.t)).\
                                filter(orm.uatrains.E.id == prepared_eid).one()
                            l = layout.getStation(s, s.s_ts, lng)
                        except:
                            notifier.notify('Uatrains error', 'Can\'t find station by id = ' + str(prepared_eid) + '\n' +\
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
    def getroute(self, rid=-1, is_reverse=False, tid=-1, sid=-1, lng='_ru'):
        return self.route(rid, is_reverse, tid, sid, lng)
    @cherrypy.expose
    def route(self, rid=-1, is_reverse=False, tid=-1, sid=-1, lng='_ru'):
        cherrypy.response.status = 301
        location = '/'
        try:
            if int(tid) > 0:
                location = '/t/' + str(tid)
            elif int(sid) > 0:
                location = '/s/' + str(sid)
        except:
            pass
        cherrypy.response.headers['Location'] = location
        return ''
    @cherrypy.expose
    def getstation(self, sid):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/s/' + str(sid)
        return ''
    @cherrypy.expose
    def station(self, sid):
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
                if s.oid > station.oid:
                    s = station
            id = s.id
        except:
            notifier.notify('Uatrains error', 'Can\'t find station by sid = ' + str(sid) + '\n' +\
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
    def gettrain(self, tid):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = '/t/' + str(tid)
        return ''
    @cherrypy.expose
    def train(self, tid):
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
                if t.oid > train.oid:
                    t = train
            id = t.id
        except:
            notifier.notify('Uatrains error', 'Can\'t find train by tid = ' + str(tid) + '\n' +\
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
            q = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == etype.station).filter(orm.or_(orm.or_(
                orm.uatrains.E.ua_title.ilike('%' + ph.lower() + '%'),
                orm.uatrains.E.ru_title.ilike('%' + ph.lower() + '%')),
                orm.uatrains.E.en_title.ilike('%' + ph.lower() + '%'))).\
                order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            ss = q.limit(pc).offset(pn * pc).all()
            next_p_ss = q.limit(pc).offset((pn + 1) * pc).all()
            if len(next_p_ss) > 0:
                has_next_p = True
        except Exception:
            notifier.notify('Uatrains error', 'Can\'t find stations\n' + traceback.format_exc())
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
                q = ses.query(orm.uatrains.E).filter(orm.and_(orm.uatrains.E.etype == etype.train,
                    orm.uatrains.E.ua_title.ilike('%' + ph.lower() + '%'))).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            if lng == lngs.RU:
                q = ses.query(orm.uatrains.E).filter(orm.and_(orm.uatrains.E.etype == etype.train,
                    orm.uatrains.E.ru_title.ilike('%' + ph.lower() + '%'))).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.ru_title)
            if lng == lngs.EN:
                q = ses.query(orm.uatrains.E).filter(orm.and_(orm.uatrains.E.etype == etype.train,
                    orm.uatrains.E.en_title.ilike('%' + ph.lower() + '%'))).\
                    order_by(orm.uatrains.E.vc.desc(), orm.uatrains.E.en_title)
            ts = q.limit(pc).offset(pn * pc).all()
            next_p_ts = q.limit(pc).offset((pn + 1) * pc).all()
            if len(next_p_ts) > 0:
                has_next_p = True
        except Exception:
            notifier.notify('Uatrains error', 'Can\'t find trains\n' + traceback.format_exc())
        ses.close()
        conn.close()
        return layout.getTrains(ts, ph, pn, has_next_p, lng)
    @cherrypy.expose
    def es(self, ph='', pn=0):
        lng = get_lng()
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        pn = int(pn)
        pc = 9
        es = []
        has_next_p = False
        prepared_ph = ph.replace(' ', '%').replace('-', '%')
        try:
            q = ses.query(orm.uatrains.E).filter(orm.or_(orm.or_(orm.or_(
                orm.uatrains.E.ua_title.ilike('%' + prepared_ph.lower() + '%'),
                orm.uatrains.E.ru_title.ilike('%' + prepared_ph.lower() + '%')),
                orm.uatrains.E.en_title.ilike('%' + prepared_ph.lower() + '%')),
                orm.uatrains.E.value.op('similar to')('([0-9А-Яа-я]*/)?' + prepared_ph.lower() + \
                    '([А-Яа-я]*)?(/[0-9А-Яа-я]*)?(/[0-9А-Яа-я]*)?'))).\
                order_by(orm.uatrains.E.etype.desc(), orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            es = q.limit(pc).offset(pn * pc).all()
            next_p_es = q.limit(pc).offset((pn + 1) * pc).all()
            if len(next_p_es) > 0:
                has_next_p = True
        except Exception:
            notifier.notify('Uatrains error', 'Can\'t find entities\n' + traceback.format_exc())
        ses.close()
        conn.close()
        return layout.getEs(es, ph, pn, has_next_p, lng)
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
            notifier.notify('Uatrains error', 'Can\'t find news\n' + traceback.format_exc())
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
    @cherrypy.expose
    def get_railway_timetable(self, rwid):
        lng = 'RU'
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        rw = None
        l = ''
        try:
            rw = ses.query(orm.uatrains.Railway).\
                options(orm.joinedload_all(orm.uatrains.Railway.routes, orm.uatrains.Route.route_trains,
                    orm.uatrains.RouteTrain.train,
                orm.uatrains.E.t_ss)).\
                filter(orm.uatrains.Railway.id == int(rwid)).all()
        except:
            notifier.notify('Uatrains error', 'Can\'t find railway by rwid = ' + str(rwid) + '\n' +\
                traceback.format_exc())
        if rw is not None:
            if rw[0].routes is None or (rw[0].routes is not None and len(rw[0].routes) == 0):
                notifier.notify('Uatrains error', 'No routes were found for rwid = ' + str(rwid))
            l = layout.getRailwayTimetable(rw[0], lng)
        ses.close()
        conn.close()
        return l

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