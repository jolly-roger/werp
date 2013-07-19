import traceback

from werp import orm, nlog

def full(ses, ph, pc, pn):
    es = []
    has_next_p = False
    prepared_ph = ph.replace(' ', '%').replace('-', '%')
    try:
        q = ses.query(orm.uatrains.E).\
            filter(orm.and_(orm.or_(orm.uatrains.E.ua_title.ilike('%' + prepared_ph.lower() + '%'),
                orm.uatrains.E.ru_title.ilike('%' + prepared_ph.lower() + '%'),
                orm.uatrains.E.en_title.ilike('%' + prepared_ph.lower() + '%'),
                orm.uatrains.E.ua_graph.ilike('%' + prepared_ph.lower() + '%'),
                orm.uatrains.E.ru_graph.ilike('%' + prepared_ph.lower() + '%'),
                orm.uatrains.E.en_graph.ilike('%' + prepared_ph.lower() + '%'),
                orm.uatrains.E.value.op('similar to')('([0-9А-Яа-я]*/)?' + prepared_ph.lower() + \
                    '([А-Яа-я]*)?(/[0-9А-Яа-я]*)?(/[0-9А-Яа-я]*)?')),
                orm.uatrains.E.ref_id == None)).\
            order_by(orm.uatrains.E.etype.desc(), orm.uatrains.E.vc.desc(), orm.uatrains.E.ua_title)
        es = q.limit(pc).offset(pn * pc).all()
        next_p_es = q.limit(pc).offset((pn + 1) * pc).all()
        if len(next_p_es) > 0:
            has_next_p = True
    except Exception:
        nlog.info('Uatrains error', 'Can\'t find entities\n' + traceback.format_exc())
    return es, has_next_p

def from_to(ses, fs, ts, pc, pn):
    es = []
    has_next_p = False
    if fs != '' and ts == '':
        es, has_next_p = full(ses, fs.replace(' ', '%').replace('-', '%'), pc, pn)
    elif fs == ''and ts != '':
        es, has_next_p = full(ses, ts.replace(' ', '%').replace('-', '%'), pc, pn)
    else:
        prepared_fs = fs.replace(' ', '%').replace('-', '%')
        prepared_ts = ts.replace(' ', '%').replace('-', '%')
        prepared_ph = prepared_fs + '%' + prepared_ts
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