import logging
import logging.handlers

class WerpSMTPHandler(logging.handlers.SMTPHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
    def getSubject(self, record):
        if hasattr(record, 'subj'):
            return record.subj
        else:
            return super().getSubject(record)

nlog = logging.getLogger('werp_notification')
nlog.setLevel(logging.DEBUG)
nlog_fh = WerpSMTPHandler('localhost', 'www@dig-dns.com (www)', 'roger@dig-dns.com', 'werp notification')
nlog_fh.setLevel(logging.DEBUG)
nlog_formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
nlog_fh.setFormatter(nlog_formatter)
nlog.addHandler(nlog_fh)