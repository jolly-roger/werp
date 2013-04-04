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

class WerpLogger(object):
    def __init__(self):
        self._nlog = logging.getLogger('werp_notification')
        self._nlog.setLevel(logging.DEBUG)
        _nlog_fh = WerpSMTPHandler('localhost', 'www@dig-dns.com (www)', 'roger@dig-dns.com', 'werp notification')
        _nlog_fh.setLevel(logging.DEBUG)
        _nlog_formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
        _nlog_fh.setFormatter(_nlog_formatter)
        self._nlog.addHandler(_nlog_fh)
    def debug(subj, msg):
        self._nlog.debug(msg, extra={'subj': subj})
    def info(subj, msg):
        self._nlog.info(msg, extra={'subj': subj})
    def warning(subj, msg):
        self._nlog.warning(msg, extra={'subj': subj})
    def error(subj, msg):
        self._nlog.error(msg, extra={'subj': subj})
    def critical(subj, msg):
        self._nlog.critical(msg, extra={'subj': subj})

nlog = WerpLogger()