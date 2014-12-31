import requests
import uuid
import os
import copy

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
	self._status_filter = filters.StatusFilter()
        self._zone_filter   = filters.ZoneFilter()

	super(SimpleScheduler,self).__init__()
	
    def run_instance(self,
		     project_id,
		     user_id,
                     image_id,
                     repos,
                     branch,
		     env,
		     user_key,
                     zone_id):
	"""schedule the instance for creation and handle creating the DB entry."""

        """
        get zone where container will be in.
        #FIXME zone should be get from database by zone_id
        #TODO  add get_zone(zone_id) 
        """
        if zone_id == 0:
            self.zone = 'BJ'
        elif zone_id == 1:
            self.zone = 'CD' 
        else:
            self.zone = 'BJ' 

        """filter and weighted hosts"""
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
	    if self._passes_zone_filter(host):
                if self._passes_status_filter(host):
		    filtered_hosts.append(host)
	return filtered_hosts

    def _passes_zone_filter(self,host):
	return self._zone_filter.host_passes(host,self.zone)

    def _passes_status_filter(self,host):
        return self._status_filter.host_passes(host)

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
        project = self.db.get_project(project_id)
        if not project:
            LOG.error("no such project %s" % project_id)
            return Response(404)
        self.db.add_container(dict(
                id=db_id,
                name=name,
                env=env,
                repos=repos,
                branch=branch,
                image_id=image_id,
                user_id=user_id,
                host_id=host_id,
                status="building"),
                project=project)
    def cleanup_db(self,id):
	"""
	remove record from db.
	"""
	self.db.delete_container(id)	
