import requests
import json
import os

from jae.common import cfg
from jae.common.cfg import Int, Str
from jae.common import client
from jae.common import log as logging

CONF=cfg.CONF
LOG=logging.getLogger(__name__)

_DEFAULT_DOCKER_HOST = 'localhost'
_DEFAULT_DOCKER_PORT = 4234

class API(object):
    def __init__(self):
        self.host = _DEFAULT_DOCKER_HOST 
        if CONF.host:
            self.host = Str(CONF.host)

        self.port = _DEFAULT_DOCKER_PORT
        if CONF.port:
            self.port = Int(CONF.port)

        self.http = client.HTTPClient()

    def create(self,name,kwargs):
	"""
	Create a container with `name` and `kwargs`.
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
        Inspect image info according to `uuid`.
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
	Pull image from image registry.
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
	Start a container with kwargs specified by uuid.
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
         """Stop the container specified by uuid"""
         #TODO(nmg): exceptions should be catched.
         #response = requests.post("http://%s:%s/containers/%s/stop" % (self.host,self.port,uuid))
         response = self.http.post("http://%s:%s/containers/%s/stop?t=5" % (self.host,self.port,uuid))
         return response.status_code

    def delete(self,uuid):
         """Delete the container uuid"""
         #TODO(nmg): exceptions should be catched.
         #response = requests.delete("http://%s:%s/containers/%s" % (self.host,self.port,uuid))
         response = self.http.delete("http://%s:%s/containers/%s?force=1" % (self.host,self.port,uuid))
         return response.status_code
    
    def inspect(self,uuid):
        """Inspect a container by uuid."""
        # TODO(nmg): exceptions should be catched.
        #response = requests.get("http://%s:%s/containers/%s/json" % \
        #                       (self.host,self.port,uuid))
        response = self.http.get("http://%s:%s/containers/%s/json" % \
                               (self.host,self.port,uuid))
        if response.status_code != 200:
            return {} 
        return response.json()
    def refresh(self,
                uuid,
                user_id,
                repos,
                branch,
                mercurial):
        """
        Refresh code in container
        
        The container code is placed in the following path:
        >>>/home/jae/{user_id}/{uuid}/www/{repos}<<< 
        """ 
        root_path = "/home/jae/%s/%s/www" % (user_id,uuid[:12]) 
        repo_path = repos
        try:
            mercurial.pull(root_path,repo_path)   
        except:
            LOG.error("Pull code failed for code sync")
            raise

        try:
            mercurial.update(root_path,repo_path,branch)
        except:
            LOG.error("Update code failed for code sync")
            raise
        
