import logging
import logging.handlers

class WerpSMTPHandler(logging.handlers.SMTPHandler):
    def __init__(self):
        super().__init__()
    def getSubject(self, record):
        appName = record.name.split('.')[-1]
        return appName


elog = logging.getLogger('werp_error')
elog.setLevel(logging.DEBUG)
elog_fh = WerpSMTPHandler('localhost', 'www@dig-dns.com (www)', 'roger@dig-dns.com', 'werp error')
elog_fh.setLevel(logging.DEBUG)
elog_formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s %(message)s')
elog_fh.setFormatter(elog_formatter)
elog.addHandler(elog_fh)