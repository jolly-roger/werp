import traceback
import json

from werp import orm
from werp import nlog

try:
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    logs = ses.query(orm.Log).filter(orm.Log.is_parsed == False).all()
    for log in logs:
        log.is_parsed = True
        ev = None
        try:
            ev = json.loads(log.value)
        except:
            nlog.info('req_logger - load log value error', str(log.value) + '\n' + traceback.format_exc())
        if ev is not None:
            try:
                user_agent = ses.query(orm.UserAgent).filter(orm.UserAgent.value == ev['HTTP_USER_AGENT']).one()
            except orm.NoResultFound:
                user_agent = orm.UserAgent(ev['HTTP_USER_AGENT'])
                ses.add(user_agent)
    ses.commit()
    ses.close()
    conn.close()
except:
    nlog.info('req_logger - parser error', traceback.format_exc())