from jae.scheduler import scheduler
from jae.common import exception

class SchedulerManager(object):
    def __init__(self):
	self.driver = scheduler.SimpleScheduler()
    def run_instance(self,body):
	try:
	    self.driver.run_instance(body)
	except exception.NoValidHost:
	    raise
