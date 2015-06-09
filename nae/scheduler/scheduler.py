import requests
import uuid
import os
import copy

from requests import ConnectionError
from operator import attrgetter
from nae.common import exception
from nae.common import log as logging
from nae.common.response import ResponseObject,Response
from nae.common import utils

from nae.scheduler import driver
from nae.scheduler import filters
from nae.scheduler.host import WeightedHost

LOG = logging.getLogger(__name__)

class SimpleScheduler(driver.Scheduler):
    """
    Very simple scheduler scheduling by the quantity of the containers.
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
	"""
        Schedule the instance for creation and handle creating the DB entry."""

        """
        Get zone where container will be in.
        """
        self.zone = self.get_zone(zone_id) 
        """Filter and weighted hosts"""
	weighted_hosts = self._scheduler()
	for host in weighted_hosts:
	    print host.addr,host.port,host.weight
        try:
	    weighted_host = weighted_hosts.pop(0)
	except IndexError:
	    raise exception.NoValidHost("No valid host was found")

	host,port = weighted_host.addr,weighted_host.port

	""" The host id where the container will be on."""
	host_id = weighted_host.id

	""" The unique container uuid"""
        db_id         = uuid.uuid4().hex

        
	"""Generate container name"""
        name = name = self.get_random_name()
	"""
	Insert db a record for instance create.
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
	except ConnectionError as ex:
	    LOG.error(ex)
	    """Post failed,cleanup db record."""
	    self.cleanup_db(db_id)

	    """Raise error to controller"""
	    raise 

	return {"id": db_id} 

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
	"""Creating db entry for creation"""
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
	Remove record from db.
	"""
	self.db.delete_container(id)	

    def get_random_name(self):
        return utils.random_str(10)

    def get_zone(zone_id):
        # FIXME: zone should be get from database by zone_id
        if zone_id == 0:
            zone = 'BJ'
        if zone_id == 1:
            zone = 'CD' 
        return zone

