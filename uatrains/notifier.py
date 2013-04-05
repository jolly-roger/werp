import smtplib
from email.mime.text import MIMEText


def notify(subject, message):
    sender = 'www@dig-dns.com (www)'
    recipient = 'roger@dig-dns.com'

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()
    
    return 'Error'