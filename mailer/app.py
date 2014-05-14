import smtplib
import os
import os.path
import datetime
from email.mime.text import MIMEText

from werp.common import constants

def sendmail(subject, message):
    sender = 'www@dig-dns.com (www)'
    recipient = 'roger@dig-dns.com'
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()
    
today = datetime.date.today()
yday = datetime.date(today.year, today.month, (today.day - 1))

# froxly grabber
y_froxly_grabber_log = constants.LOGS_DIR + '/froxly_grabber.log.' + yday.isoformat()
if os.path.isfile(y_froxly_grabber_log):
    l = open(y_froxly_grabber_log)
    m = l.read()
    l.flush()
    l.close()
    sendmail('froxly grabber report for ' + yday.isoformat(), m)
    os.remove(y_froxly_grabber_log)
    
# froxly checker
y_froxly_checker_log = constants.LOGS_DIR + '/froxly_checker.log.' + yday.isoformat()
if os.path.isfile(y_froxly_checker_log):
    l = open(y_froxly_checker_log)
    m = l.read()
    l.flush()
    l.close()
    sendmail('froxly checker report for ' + yday.isoformat(), m)
    os.remove(y_froxly_checker_log)