import requests
from jae.common import cfg
from jae.common import log as logging

from jae.common.cfg import Str, Int
import requests

CONF=cfg.CONF
LOG=logging.getLogger(__name__)

class API(object):
    def __init__(self):
	self.endpoint = CONF.service_endpoint
        self.headers={'Content-Type':'application/json'}

    def create(self,name,data):
        _url = "%s/images/create?name=%s" % \
               (self.endpoint,name)
        return requests.post(_url,
		    data=data)
	
    def inspect(self,name):
        _url = "%s/images/%s/json" % \
	       (self.endpoint,name)
        response=requests.get(_url)
        return response.status_code,response.json()

    def build(self,name,data):
        _url = "%s/build?t=%s" % \
               (self.endpoint,name)
        headers={'Content-Type':'application/tar'}
        response = requests.post(_url,headers=headers,data=data)
        return response.status_code

    def delete(self,repository,tag):
        image_registry_endpoint = CONF.image_registry_endpoint
        if not image_registry_endpoint:
            LOG.error('no registry endpoint found!')
            return 404
	if not image_registry_endpoint.startswith("http://"):
	    image_registry_endpoint += "http://"
	response=requests.delete("%s/v1/repositories/%s/tags/%s" % \
				(image_registry_endpoint,repository,tag))
	return response.status_code

    def tag(self,name):
	image_registry_endpoint = CONF.image_registry_endpoint
        if not image_registry_endpoint:
            LOG.error('no registry endpoint found!')
            return 404
	if image_registry_endpoint.startswith("http://"):
	    image_registry_endpoint = image_registry_endpoint.replace("http://","")
	host = Str(CONF.host)
        port = Int(CONF.port)
	response=requests.post("%s:%s/v1/images/%s/tag?repo=%s&force=0&tag=latest" 
                       % (host,port,name,image_registry_endpoint))
	return response.status_code
