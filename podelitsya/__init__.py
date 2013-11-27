from . import app

app = app.wsgi()

import logging
import logging.handlers

from werp.common import constants

logger = logging.getLogger('podelitsya')
logger.setLevel(logging.DEBUG)
logger_fh = logging.handlers.TimedRotatingFileHandler(constants.LOGS_DIR + '/podelitsya.log', when='midnight')
logger_fh.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('[%(asctime)s] %(message)s')
logger_fh.setFormatter(logger_formatter)
logger.addHandler(logger_fh)