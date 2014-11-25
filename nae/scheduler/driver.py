import requests
import json
from nae import db

class Scheduler(object):
    def __init__(self):
	self.db = db.API()

    def run_instance():
	msg = "Driver must implement run_instance"
	raise NotImplementedError(msg)

    def post(self,host,port,body):
	if not isinstance(body,json):
	    body = json.dumps(body) 
        return requests.post("http://%s:%s/containers/create" % (host,port),
			     headers = '{Content-Type:application/json}',
			     data = body) 
