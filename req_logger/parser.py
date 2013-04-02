import smtplib
from email.mime.text import MIMEText
import traceback
import json

from werp import orm

try:
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    entries = ses.query(orm.Entry).filter(orm.Entry.is_parsed == False).all()
    for entry in entries:
        ev = json.loads(entry.value)
        try:
            user_agent = ses.query(orm.UserAgent).filter(orm.UserAgent.value == ev['HTTP_USER_AGENT']).one()
        except orm.NoResultFound:
            user_agent = orm.UserAgent(ev['HTTP_USER_AGENT'])
            ses.add(user_agent)
            entry.is_parsed = True
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