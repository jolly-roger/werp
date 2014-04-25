import logging
import logging.handlers

from .common import constants

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
    def debug(self, subj, msg):
        self._nlog.debug(msg, extra={'subj': subj})
    def info(self, subj, msg):
        self._nlog.info(msg, extra={'subj': subj})
    def warning(self, subj, msg):
        self._nlog.warning(msg, extra={'subj': subj})
    def error(self, subj, msg):
        self._nlog.error(msg, extra={'subj': subj})
    def critical(self, subj, msg):
        self._nlog.critical(msg, extra={'subj': subj})

nlog = WerpLogger()

exec_log = logging.getLogger('exec')
exec_log.setLevel(logging.DEBUG)
_exec_log_fh = logging.handlers.RotatingFileHandler(constants.LOGS_DIR + '/exec.log', maxBytes=1048576)
_exec_log_fh.setLevel(logging.DEBUG)
_exec_log_formatter = logging.Formatter('[%(asctime)s] %(message)s')
_exec_log_fh.setFormatter(_exec_log_formatter)
exec_log.addHandler(_exec_log_fh)

error_log = logging.getLogger('error')
error_log.setLevel(logging.DEBUG)
_error_log_fh = logging.handlers.RotatingFileHandler(constants.LOGS_DIR + '/error.log', maxBytes=1048576)
_error_log_fh.setLevel(logging.DEBUG)
_error_log_formatter = logging.Formatter('[%(asctime)s] %(message)s')
_error_log_fh.setFormatter(_error_log_formatter)
error_log.addHandler(_error_log_fh)

# froxly
froxly_grabber_log = logging.getLogger('froxly_grabber')
froxly_grabber_log.setLevel(logging.DEBUG)
_froxly_grabber_fh = logging.handlers.RotatingFileHandler(constants.LOGS_DIR + '/froxly_grabber.log', maxBytes=1048576)
_froxly_grabber_fh.setLevel(logging.DEBUG)
_froxly_grabber_formatter = logging.Formatter('[%(asctime)s] %(message)s')
_froxly_grabber_fh.setFormatter(_froxly_grabber_formatter)
froxly_grabber_log.addHandler(_froxly_grabber_fh)
