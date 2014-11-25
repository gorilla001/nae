import requests
from operator import attrgetter
from nae.common import exception

from nae.scheduler import driver
from nae.scheduler.host import WeightedHost

class SimpleScheduler(driver.Scheduler):
    """
    very simple scheduler scheduling by the quantity of the containers.
    """
    def __init__(self):
	super(SimpleScheduler,self).__init__()
	
    def run_instance(self,body):
	weighted_hosts = self._scheduler()
        try:
	    weighted_host = weighted_hosts.pop(0)
	except IndexError:
	    raise exception.NoValidHost("No valid host was found")
	host,port = weighted_host.addr,weighted_host.port
	try:
	    self.post(host,port,body)
	except:
	    raise
    
    def delete_instance(self,id):
	pass
	
    def _scheduler(self):
	selected_hosts = []
	unweighted_host = self.db.get_hosts()
	for host in unweighted_host:
	    weight=self.get_weight(host.id)
	    weighted_host = WeightedHost(weight,
				         host.host,
					 host.port)
		
	    selected_hosts.append(weighted_host)

	selected_hosts.sort(key=attrgetter('weight'))
	return selected_hosts

    def get_weight(self,host):
	containers = self.db.get_containers_by_host(host_id)
	weight = len(containers)

	return weight	
