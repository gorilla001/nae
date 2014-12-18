import requests
import uuid
import os

from requests import ConnectionError
from operator import attrgetter
from jae.common import exception
from jae.common import log as logging
from jae.common.response import ResponseObject,Response

from jae.scheduler import driver
from jae.scheduler import filters
from jae.scheduler.host import WeightedHost

LOG = logging.getLogger(__name__)

class SimpleScheduler(driver.Scheduler):
    """
    very simple scheduler scheduling by the quantity of the containers.
    """
    def __init__(self):
	self.filter = filters.StatusFilter()

	super(SimpleScheduler,self).__init__()
	
    def run_instance(self,
		     project_id,
		     user_id,
                     image_id,
                     repos,
                     branch,
		     env,
		     user_key):
	"""schedule the instance for creation and handle creating the DB entry."""

	weighted_hosts = self._scheduler()
	for host in weighted_hosts:
	    print host.addr,host.port,host.weight
        try:
	    weighted_host = weighted_hosts.pop(0)
	except IndexError:
	    raise exception.NoValidHost("No valid host was found")

	host,port = weighted_host.addr,weighted_host.port

	""" the host id where the container will be on."""
	host_id = weighted_host.id

	""" the unique container uuid"""
        db_id         = uuid.uuid4().hex

	""" get fixed ip from ip resource pool
	fixed_ip = self.network.get_fixed_ip()

	print fixed_ip
	body['fixed_ip'] = fixed_ip
	"""

	"""generate container name"""
	name   = os.path.basename(repos) + '-' + branch
        query  = self.db.get_containers()
        count  = len(query)
        suffix = count +1
        name   = name + '-' + str(suffix).zfill(8)
	"""
	insert db a record for instance create.
	"""
	self.save_to_db(db_id,
			name,
			env,
			project_id,
			repos,
			branch,
			image_id,
			user_id,
			host_id)
	try:
	    self.post(host,
	              port,
	              db_id=db_id,
	              name=name,
                      env=env,
                      project_id=project_id,
                      repos=repos,
                      branch=branch,
                      image_id=image_id,
                      user_id=user_id,
                      user_key=user_key)
	except ConnectionError,err:
	    LOG.error(err)
	    """post failed,cleanup db record."""
	    self.cleanup_db(db_id)

	    """raise error to controller"""
	    raise 

	return {"id":db_id} 

    def delete_instance(self,id):
	pass
	
    def _scheduler(self):
	selected_hosts = []
	unfiltered_hosts = self.db.get_hosts()
	filtered_hosts = self._filter_hosts(unfiltered_hosts)

	if not filtered_hosts:
	    raise exception.NoValidHost("No valid host was found")

	unweighted_host = filtered_hosts 
	for host in unweighted_host:
	    weight=self.get_weight(host.id)
	    weighted_host = WeightedHost(host.id,
					 weight,
				         host.host,
					 host.port)
		
	    selected_hosts.append(weighted_host)

	selected_hosts.sort(key=attrgetter('weight'))
	
	return selected_hosts

    def _filter_hosts(self,hosts):
	filtered_hosts = []
	for host in hosts:
	    if self._passes_filters(host):
		filtered_hosts.append(host)
	return filtered_hosts

    def _passes_filters(self,host):
	return self.filter.host_passes(host)

    def get_weight(self,host_id):
	containers = self.db.get_containers_by_host(host_id)
	weight = len(containers)

	return weight	

    def save_to_db(self,
		   db_id,
		   name,
		   env,
		   project_id,
		   repos,
		   branch,
		   image_id,
		   user_id,
		   host_id):
	"""creating db entry for creation"""
	"""
	db_id      = body.get('db_id')
	image_id   = body.get('image_id')
        image_uuid = body.get('image_uuid')
        repository = body.get('repository')
        tag        = body.get('tag')
        env        = body.get('env')
        project_id = body.get('project_id')
        repos      = body.get('repos')
        branch     = body.get('branch')
        app_type   = body.get('app_type')
        user_id    = body.get('user_id')
        user_key   = body.get('user_key')
        host_id    = body.get('host_id')
	name	   = body.get('name')
	fixed_ip   = body.get('fixed_ip')
	"""
        self.db.add_container(dict(
                id=db_id,
                name=name,
                env=env,
                project_id=project_id,
                repos=repos,
                branch=branch,
                image_id=image_id,
                user_id=user_id,
                host_id=host_id,
		##fixed_ip=fixed_ip,
                status="building"))
    def cleanup_db(self,id):
	"""
	remove record from db.
	"""
	self.db.delete_container(id)	
