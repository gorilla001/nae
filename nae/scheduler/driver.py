
from nae import db

class Scheduler(object):
    def __init__(self):
	self.db = db.API()

    def run_instance():
	msg = "Driver must implement run_instance"
	raise NotImplementedError(msg)
