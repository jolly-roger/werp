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
    trains = ses.query(orm.uatrains.E).\
        filter(orm.or_(orm.uatrains.E.etype == 1, orm.uatrains.E.etype == 4, orm.uatrains.E.etype == 5)).all()
    for t in trains:
        if len(t.t_ss) > 0:
            ua_graph = ''
            ru_graph = ''
            en_graph = ''
            for ts in t.t_ss:
                ua_graph += ts.s.ua_title.lower() + '; '
                ru_graph += ts.s.ru_title.lower() + '; '
                en_graph += ts.s.en_title.lower() + '; '
            t.ua_graph = ua_graph
            t.ru_graph = ru_graph
            t.en_graph = en_graph
            ses.commit()
    ses.close()
    conn.close()
    end_time = time.time()
    exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
    exec_log.info('uatrains bot grapher %s %s' % (str(start_dt), str(exec_delta)))
except:
    if ses is not None:
        ses.close()
    if conn is not None:
        conn.close()
    nlog.info('uatrains bot - grapher fatal', traceback.format_exc())