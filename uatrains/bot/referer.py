from datetime import datetime
import traceback

from werp import orm, nlog

conn = None
ses = None
try:
    conn = orm.null_engine.connect()
    ses = orm.sescls(bind=conn)
    etrains = ses.query(orm.uatrains.E).filter(orm.uatrains.E.etype == 1).all()
    for et in etrains:
        if et.ref_id is None:
            if (et.from_date is None and et.to_date is None) or \
                (et.from_date is not None and et.to_date is not None and not (\
                    et.from_date <= datetime.now() and \
                    et.to_date >= datetime.now())):
                last_etrain = et
                similar_etrains = ses.query(orm.uatrains.E).\
                    filter(orm.and_(orm.uatrains.E.value == et.value, orm.uatrains.E.ua_title == et.ua_title,
                        orm.uatrains.E.ru_title == et.ru_title, orm.uatrains.E.en_title == et.en_title,
                        orm.uatrains.E.etype == 1)).all()
                if len(similar_etrains) > 1:
                    last_etrain = similar_etrains[0]
                    for similar_et in similar_etrains:
                        if (similar_et.from_date is not None and similar_et.to_date is not None and \
                                similar_et.from_date <= datetime.now() and \
                                similar_et.to_date >= datetime.now()) and \
                            ((last_etrain.from_date is None and last_etrain.to_date is None) or \
                                (last_etrain.to_date <= similar_et.from_date) or \
                                (last_etrain.id < similar_et.id)):
                            last_etrain = similar_et
                if last_etrain.id != et.id:
                    et.ref_id = last_etrain.id
                    ses.commit()
    ses.close()
    conn.close()
except:
    if ses is not None:
        ses.close()
    if conn is not None:
        conn.close()
    nlog.info('uatrains bot - referer fatal', traceback.format_exc())