import smtplib
from email.mime.text import MIMEText
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
        ev = json.loads(log.value)
        try:
            user_agent = ses.query(orm.UserAgent).filter(orm.UserAgent.value == ev['HTTP_USER_AGENT']).one()
        except orm.NoResultFound:
            user_agent = orm.UserAgent(ev['HTTP_USER_AGENT'])
            ses.add(user_agent)
        ses.commit()
    ses.close()
    conn.close()
except:
    sender = 'www@dig-dns.com (www)'
    recipient = 'roger@dig-dns.com'

    msg = MIMEText(traceback.format_exc())
    msg['Subject'] = 'req_logger - parse log error'
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()
nlog.info('Log parsing finished', 'req logger - parser')