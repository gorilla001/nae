import requests
import json

from jae.common import cfg
from jae.common.cfg import Int, Str
from jae.common import client

CONF=cfg.CONF

_DEFAULT_DOCKER_HOST = 'localhost'
_DEFAULT_DOCKER_PORT = 4234

class API(object):
    def __init__(self):
        self.host = _DEFAULT_DOCKER_HOST 
        if not CONF.host:
            self.host = Str(CONF.host)

        self.port = _DEFAULT_DOCKER_PORT
        if not CONF.port:
            self.port = Int(CONF.port)

        self.http = client.HTTPClient()

    def create(self,name,kwargs):
	"""
	create a container with `name` and `kwargs`.
	"""
        # TODO(nmg): exceptions should be catched.
        #response = requests.post("http://%s:%s/containers/create?name=%s" \
        #                      % (self.host,self.port,name),
	#			 headers = {'Content-Type':'application/json'},
	#			 data = json.dumps(kwargs))
        response = self.http.post("http://%s:%s/containers/create?name=%s" \
                              % (self.host,self.port,name),
				 headers = {'Content-Type':'application/json'},
				 data = json.dumps(kwargs))
	return response

    def inspect_image(self,uuid):
        """
        inspect image info according to `uuid`.
        """

        # TODO(nmg): exceptions should be catched.
        #response = requests.get("http://%s:%s/images/%s/json" % \
	#	                 (self.host,self.port,uuid))
        try:
            response = self.http.get("http://%s:%s/images/%s/json" % \
		                 (self.host,self.port,uuid))
        except requests.ConnectionError: 
            LOG.error("Connect to %s:%s failed" % (self.host,self.port))
            raise
            
	return response

    def pull_image(self,repository,tag):
	"""
	pull image from image registry.
	"""
	image_registry_endpoint = CONF.image_registry_endpoint
	if not image_registry_endpoint:
	    LOG.error('no registry endpoint found!')
	    return 404 
	host = Str(CONF.host) or _DEFAULT_DOCKER_HOST 
	port = Int(CONF.port) or _DEFAULT_DOCKER_PORT 
	url = "http://%s:%s/images/create" % (host,port)
	from_image = image_registry_endpoint + "/" + "%s:%s" % (repository,tag)	
	
        # TODO(nmg): exceptions should be catched.
	#response = requests.post("%s?fromImage=%s" % (url,from_image))
	response = self.http.post("%s?fromImage=%s" % (url,from_image))
        return response.status_code

    def start(self,uuid,kwargs):
	"""
	start a container with kwargs specified by uuid.
	"""
        # TODO(nmg): exceptions should be catched.
	#response = requests.post("http://%s:%s/containers/%s/start" % (self.host,self.port,uuid),
	#			 headers = {'Content-Type':'application/json'},
	#			 data = json.dumps(kwargs))
	response = self.http.post("http://%s:%s/containers/%s/start" % (self.host,self.port,uuid),
				 headers = {'Content-Type':'application/json'},
				 data = json.dumps(kwargs))
				
	return response.status_code

    def stop(self,uuid):
         """stop the container specified by uuid"""
         #TODO(nmg): exceptions should be catched.
         #response = requests.post("http://%s:%s/containers/%s/stop" % (self.host,self.port,uuid))
         response = self.http.post("http://%s:%s/containers/%s/stop" % (self.host,self.port,uuid))
         return response.status_code

    def delete(self,uuid):
         """delete the container uuid"""
         #TODO(nmg): exceptions should be catched.
         #response = requests.delete("http://%s:%s/containers/%s" % (self.host,self.port,uuid))
         response = self.http.delete("http://%s:%s/containers/%s" % (self.host,self.port,uuid))
         return response.status_code
    
    def inspect(self,uuid):
        """inspect a container by uuid."""
        # TODO(nmg): exceptions should be catched.
        #response = requests.get("http://%s:%s/containers/%s/json" % \
        #                       (self.host,self.port,uuid))
        response = self.http.get("http://%s:%s/containers/%s/json" % \
                               (self.host,self.port,uuid))
        if response.status_code != 200:
            return {} 
        return response.json()
    def refresh(self,
                user_id,
                repos,
                branch,
                mercurial):
        """"refresh code in container."""
        try:
            mercurial.pull(user_id,repos)   
        except:
            raise

        try:
            mercurial.update(user_id,repos,branch)
        except:
            raise
        
