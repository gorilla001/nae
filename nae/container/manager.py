import requests

from nae.common import cfg
from nae.common import log as logging
from nae.scheduler import manager

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Manager(object):
    def __init__(self):
	self._scheduler = manager.SchedulerManager()

    def create(self,body):
        self._scheduler.run_instance(body)	

    def delete(self,id):
        self._scheduler.scheduler("DELETE",id)

