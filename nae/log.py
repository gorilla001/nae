import logging 
from nae.common import cfg

CONF=cfg.CONF

def getlogger():
    logger=logging.getLogger('eventlet.wsgi.server')
    hdlr=logging.FileHandler(CONF.log_file)
    formatter=logging.Formatter(CONF.log_format,CONF.log_date_format)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)

    return logger

class WSGILogger(object):
    def __init__(self,logger,level=logging.INFO):
        self.logger = logger
        self.level = level 

    def write(self, msg):
        self.logger.log(self.level, msg.rstrip())
