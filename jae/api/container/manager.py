import requests

from jae.common import cfg
from jae.common import log as logging
from jae.scheduler import manager

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Manager(object):
    def __init__(self):
	self._scheduler = manager.SchedulerManager()

    def create(self,body):
        instance = self._scheduler.run_instance(body)	
	return instance

    def delete(self,id):
	pass	

