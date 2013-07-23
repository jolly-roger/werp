import traceback
import time
import datetime

from werp import orm, nlog, exec_log

conn = None
ses = None
try:
    start_dt = datetime.datetime.now()
    start_time = time.time()
    conn = orm.null_engine.connect()
    ses = orm.sescls(bind=conn)
    etrains = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == 5).all()
    for et in etrains:
        if et.ref_id is None:
            if (et.from_date is None and et.to_date is None) or \
                (et.from_date is not None and et.to_date is not None and not (\
                    et.from_date <= datetime.datetime.now() and \
                    et.to_date >= datetime.datetime.now())):
                last_etrain = et
                similar_etrains = ses.query(orm.uatrains.E).\
                    filter(orm.and_(orm.uatrains.E.oid == et.oid,
                        orm.uatrains.E.ua_title == et.ua_title, orm.uatrains.E.ru_title == et.ru_title,
                        orm.uatrains.E.etype == 5)).all()
                if len(similar_etrains) > 1:
                    for similar_et in similar_etrains:
                        if similar_et.c_date > last_etrain.c_date:
                            last_etrain = similar_et
                if last_etrain.id > et.id:
                    et.ref_id = last_etrain.id
                    ses.commit()
    ses.close()
    conn.close()
    end_time = time.time()
    exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
    exec_log.info('uatrains bot ptrain referer %s %s' % (str(start_dt), str(exec_delta)))
except:
    if ses is not None:
        ses.close()
    if conn is not None:
        conn.close()
    nlog.info('uatrains bot - ptrain referer fatal', traceback.format_exc())