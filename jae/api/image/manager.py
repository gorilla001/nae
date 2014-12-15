import requests

from jae.common import cfg
from jae.common import log as logging

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Manager(object):
    def create(self,body):
        url = CONF.image_service_endpoint
        if not url:
            LOG.error("image service endpoint must be specfied!")
            return
        requests.post(url,data=body) 

    def delete(self,id):
        url = CONF.image_service_endpoint 
        if not url:
            LOG.error("image service endpoint must be specfied!")
            return
	request_url = url + "/" + id
	requests.delete(request_url)

