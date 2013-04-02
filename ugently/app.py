import smtplib
from email.mime.text import MIMEText
import traceback

from werp import orm

from . import layout

def app(env, start_res):
    start_res('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
    l = bytes('No data', 'utf-8')
    try:
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        user_agents = []#ses.query(orm.UserAgent).all()
        l = layout.getHome(user_agents)
        ses.close()
        conn.close()
    except:
        sender = 'www@dig-dns.com (www)'
        recipient = 'roger@dig-dns.com'
    
        msg = MIMEText(traceback.format_exc())
        msg['Subject'] = 'ugently error'
        msg['From'] = sender
        msg['To'] = recipient
    
        s = smtplib.SMTP('localhost')
        s.sendmail(sender, recipient, msg.as_string())
        s.quit()
    return l
