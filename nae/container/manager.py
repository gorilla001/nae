import requests

from nae.common import cfg
from nae.common import log as logging

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Manager(object):
    def __init__(self):
	self._scheduler = Scheduler()

    def create(self,body):
        self._scheduler.scheduler("CREATED",body)	

    def delete(self,id):
        self._scheduler.scheduler("DELETE",id)

