from datetime import datetime
import traceback

from werp import orm, nlog

conn = None
ses = None
try:
    conn = orm.null_engine.connect()
    ses = orm.sescls(bind=conn)
    trains = ses.query(orm.uatrains.E).filter(orm.and_(orm.uatrains.E.id == 28,
        orm.or_(orm.uatrains.E.etype == 1, orm.uatrains.E.etype == 4,
        orm.uatrains.E.etype == 5))).all()
    for train in trains:
        halt_ids = ses.query(orm.distinct(orm.uatrains.TrainStation.s_id)).\
            filter(orm.uatrains.TrainStation.t_id == train.id).all()
        for halt_id in halt_ids:
            halts = ses.query(orm.uatrains.TrainStation).\
                filter(orm.and_(orm.uatrains.TrainStation.t_id == train.id,
                    orm.uatrains.TrainStation.s_id == halt_id[0])).all()
            if len(halts) > 1:
                newest_halt = halts[0]
                for halt in halts:
                    if halt.c_date > newest_halt.c_date:
                        newest_halt = halt
                for halt in halts:
                    if halt.c_date != newest_halt.c_date:
                        ses.delete(halt)
                ses.commit()
    ses.close()
    conn.close()
except:
    if ses is not None:
        ses.close()
    if conn is not None:
        conn.close()
    nlog.info('uatrains bot - halt cleaner fatal', traceback.format_exc())