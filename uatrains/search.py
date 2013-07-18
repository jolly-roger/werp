import traceback

from werp import orm, nlog, error_log

def from_to(ses, fs, ts):
    es = []
    has_next_p = False
    if fs != '' and ts == '':
        prepared_fs = fs.replace(' ', '%').replace('-', '%')
        prepared_ph = prepared_fs
        try:
            q = ses.query(orm.uatrains.E).\
                filter(orm.and_(
                    orm.or_(orm.uatrains.E.ua_graph.ilike('%' + prepared_ph.lower() + '%'),
                        orm.uatrains.E.ru_graph.ilike('%' + prepared_ph.lower() + '%'),
                        orm.uatrains.E.en_graph.ilike('%' + prepared_ph.lower() + '%')),
                    orm.uatrains.E.ref_id == None)).\
                order_by(orm.uatrains.E.etype.desc(), orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            es = q.limit(pc).offset(pn * pc).all()
            next_p_es = q.limit(pc).offset((pn + 1) * pc).all()
            if len(next_p_es) > 0:
                has_next_p = True
        except Exception:
            nlog.info('Uatrains error', 'Can\'t find entities by fs\n' + traceback.format_exc())
    elif fs == ''and ts != '':
        prepared_ts = ts.replace(' ', '%').replace('-', '%')
        prepared_ph = prepared_ts
        try:
            q = ses.query(orm.uatrains.E).\
                filter(orm.and_(
                    orm.or_(orm.uatrains.E.ua_graph.ilike('%' + prepared_ph.lower() + '%'),
                        orm.uatrains.E.ru_graph.ilike('%' + prepared_ph.lower() + '%'),
                        orm.uatrains.E.en_graph.ilike('%' + prepared_ph.lower() + '%')),
                    orm.uatrains.E.ref_id == None)).\
                order_by(orm.uatrains.E.etype.desc(), orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            es = q.limit(pc).offset(pn * pc).all()
            next_p_es = q.limit(pc).offset((pn + 1) * pc).all()
            if len(next_p_es) > 0:
                has_next_p = True
        except Exception:
            nlog.info('Uatrains error', 'Can\'t find entities by ts\n' + traceback.format_exc())
    else:
        prepared_fs = fs.replace(' ', '%').replace('-', '%')
        prepared_ts = ts.replace(' ', '%').replace('-', '%')
        prepared_ph = prepared_fs + '%' + prepared_ts
        
        
        error_log.info('prepared_ph: ' + prepared_ph.lower())
        
        
        try:
            q = ses.query(orm.uatrains.E).\
                filter(orm.and_(
                    orm.or_(orm.uatrains.E.ua_graph.ilike('%' + prepared_ph.lower() + '%'),
                        orm.uatrains.E.ru_graph.ilike('%' + prepared_ph.lower() + '%'),
                        orm.uatrains.E.en_graph.ilike('%' + prepared_ph.lower() + '%')),
                    orm.uatrains.E.ref_id == None)).\
                order_by(orm.uatrains.E.etype.desc(), orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
            es = q.limit(pc).offset(pn * pc).all()
            next_p_es = q.limit(pc).offset((pn + 1) * pc).all()
            if len(next_p_es) > 0:
                has_next_p = True
        except Exception:
            nlog.info('Uatrains error', 'Can\'t find entities by fs and ts\n' + traceback.format_exc())
    return es, has_next_p