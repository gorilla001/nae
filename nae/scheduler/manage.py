from nae.scheduler import scheduler

class SchedulerManager(object):
    def __init__(self):
	self.driver = scheduler.SimpleScheduler()
    def run_instance(self):
	try:
	    self.driver.run_instance()
	except exception.NoVaildHost:
	    raise
