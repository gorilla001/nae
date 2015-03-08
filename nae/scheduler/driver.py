import requests
from requests import ConnectionError
import json
from nae import db
from nae.network import manager 

class Scheduler(object):
    def __init__(self):
	self.db = db.API()
	self.network = manager.NetworkManager()

    def run_instance(self,
                     project_id,
                     user_id,
                     image_id,
                     repos,
                     branch,
                     env,
                     user_key,
                     zone_id):
        """Must override run_instance method for scheduler to work."""
	msg = "Driver must implement run_instance"
	raise NotImplementedError(msg)

    def post(self,host,port,**body):
	try:
            return requests.post("http://%s:%s/v1/containers" % (host,port),
			     headers = {'Content-Type':'application/json'},
			     data = json.dumps(body)) 
	except ConnectionError:
	    raise
