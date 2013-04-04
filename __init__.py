import logging
import logging.handlers

nlog = logging.getLogger('werp_notification')
nlog.setLevel(logging.DEBUG)
nlog_fh = logging.handlers.SMTPHandler('localhost', 'www@dig-dns.com (www)', 'roger@dig-dns.com', 'werp notification')
nlog_fh.setLevel(logging.DEBUG)
nlog_formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
nlog_fh.setFormatter(nlog_formatter)
nlog.addHandler(nlog_fh)