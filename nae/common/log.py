import sys
import logging

from nae.common import cfg

CONF=cfg.CONF

_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)8s [%(name)s] %(message)s"
_DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_loggers={}

def setup():
    _setup_logging_from_conf()

def _setup_logging_from_conf():
    log_root = getLogger()
    if CONF.log_file:
	handler = logging.FileHandler(CONF.log_file)
    else:
        handler = logging.StreamHandler(sys.stdout)
    log_root.addHandler(handler)

    fmt=CONF.log_format or _DEFAULT_LOG_FORMAT
    datefmt = CONF.log_date_format or _DEFAULT_LOG_DATE_FORMAT
    handler.setFormatter(logging.Formatter(fmt=fmt,
					   datefmt=datefmt))

    if CONF.verbose or CONF.debug:
        log_root.setLevel(logging.DEBUG)
    else:
        log_root.setLevel(logging.INFO)

def getLogger(name=None):
    if name not in _loggers: 
        _loggers[name]=logging.getLogger(name)
    return _loggers[name] 


class DefaultFormatter(logging.Formatter):
    pass
   
class WSGILogger(object):
    def __init__(self,logger,level=logging.INFO):
        self.logger = logger
        self.level = level 

    def write(self, msg):
        self.logger.log(self.level, msg.rstrip())
 
