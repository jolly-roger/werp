import logging
import logging.handlers

class WerpSMTPHandler(logging.handlers.SMTPHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
    def getSubject(self, record):
        if record.args is not None and len(record.args) > 0:
            subject = record.args[0]
        else:
            return super().getSubject(record)
        return subject


nlog = logging.getLogger('werp_error')
nlog.setLevel(logging.DEBUG)
nlog_fh = WerpSMTPHandler('localhost', 'www@dig-dns.com (www)', 'roger@dig-dns.com', 'werp error')
nlog_fh.setLevel(logging.DEBUG)
nlog_formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s %(message)s')
nlog_fh.setFormatter(nlog_formatter)
nlog.addHandler(nlog_fh)