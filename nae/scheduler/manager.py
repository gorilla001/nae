from nae.scheduler import scheduler
from nae.common import exception

class SchedulerManager(object):
    def __init__(self):
	self.driver = scheduler.SimpleScheduler()
    def create(self,body):
	try:
	    self.driver.create(body)
	except exception.NoValidHost:
	    raise
