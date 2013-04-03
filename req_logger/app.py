import smtplib
from email.mime.text import MIMEText
import traceback
import zmq

from werp import orm

ctx = zmq.Context()

puller = ctx.socket(zmq.PULL)
puller.bind("ipc:///home/www/sockets/req_logger.socket")

try:
    while True:
        message = puller.recv()
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        log = orm.Log(message.decode('utf-8').strip())
        ses.add(log)
        ses.commit()
        ses.close()
        conn.close()
except:
    sender = 'www@dig-dns.com (www)'
    recipient = 'roger@dig-dns.com'

    msg = MIMEText(traceback.format_exc())
    msg['Subject'] = 'req_logger - log error'
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()
