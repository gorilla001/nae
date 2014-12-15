import requests
from jae.common import cfg
from jae.common.cfg import Str, Int
import requests

CONF=cfg.CONF

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

    def delete(self,uuid):
	_url = "%s/images/%s" % \
               (self.endpoint,uuid)
	response = requests.delete(_url)
        return response.status_code
