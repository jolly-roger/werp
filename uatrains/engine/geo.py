#import traceback
#import urllib.request
#import urllib.parse
#from lxml import etree
#import io
#import logging
#
#
#from .lng import lngs
#from ..common import etype
#from . import etitle
#from .. import orm
#from . import src
#
#
#logger = logging.getLogger('werp_error.uatrains_spider')
#
#
#def get_geo_data():
#    ses = None
#    conn = None
#    try:
#        parser = etree.HTMLParser()
#        conn = orm.null_engine.connect()
#        ses = orm.sescls(bind=conn)
#        geo_srcs = src.get_geo_srcs(ses)
#        for geo_src in geo_srcs:
#            for lng in lngs:
#                res = urllib.request.urlopen(src.get_geo_url(geo_src, (lngs[lng],)))
#                res_data = res.read().decode('cp1251')
#                dom_tree = etree.parse(io.StringIO(res_data), parser)
#                raw_ss = dom_tree.xpath(
#                    '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/li/table[2]/tr/td/ul/li/a')
#                for raw_s in raw_ss:
#                    raw_sid_qs = urllib.parse.urlparse(raw_s.get('href'))
#                    if len(raw_sid_qs.query) > 0:
#                        raw_sid = urllib.parse.parse_qs(raw_sid_qs.query)
#                        sid = -1
#                        try:
#                            sid = int(raw_sid['sid'][0])
#                        except:
#                            logger.info('Geo station has no sid. {\'tid\': ' + str(tid) + ', \'raw sid data\': ' +\
#                                str(raw_sid) + '}')
#                            continue
#                        s = None
#                        try:
#                            s = ses.query(orm.Station).filter(orm.Station.sid == sid).one()
#                        except Exception:
#                            logger.error(traceback.format_exc())
#                        if s is not None:
#                            gstitle = None
#                            if raw_s.text is not None:
#                                gstitle = raw_s.text.strip()
#                            if s.sid > 0 and gstitle is not None:
#                                et = orm.ETitle(s.sid, s.id, etype.station, gstitle, lng)
#                                if not etitle.is_added(et, ses):
#                                    ses.add(et)
#                                elif etitle.is_changed(et, ses):
#                                    orm_et = ses.query(orm.ETitle).filter(orm.and_(orm.and_(orm.ETitle.eid == s.id,
#                                        orm.ETitle.etype == etype.station), orm.ETitle.lng == lng)).one()
#                                    orm_et.value = gstitle
#                                ses.commit()
#        ses.close()
#        conn.close()
#    except Exception:
#        logger.fatal(traceback.format_exc())
#        if ses is not None:
#            ses.commit()
#            ses.close()
#        if conn is not None:
#            conn.close()