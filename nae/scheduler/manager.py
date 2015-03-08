from nae.scheduler import scheduler
from nae.common import exception

class SchedulerManager(object):
    def __init__(self):
	self.driver = scheduler.SimpleScheduler()
    def run_instance(self,
		     project_id,
		     ):
	try:
	    self.driver.run_instance(body)
	except exception.NoValidHost:
	    raise
