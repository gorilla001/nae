import requests
from requests import ConnectionError
import json
from nae import db

class Scheduler(object):
    def __init__(self):
	self.db = db.API()

    def run_instance():
	msg = "Driver must implement run_instance"
	raise NotImplementedError(msg)

    def post(self,host,port,body):
	try:
            return requests.post("http://%s:%s/v1/containers" % (host,port),
			     headers = {'Content-Type':'application/json'},
			     data = json.dumps(body)) 
	except ConnectionError:
	    raise
