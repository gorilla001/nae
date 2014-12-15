import webob.exc
import eventlet
import uuid
import os

from jae import wsgi
from jae.base import Base
from jae.common.mercu import MercurialControl
from jae.common import log as logging
from jae.common.view import View
from jae.common.response import Response
from jae.common import cfg
from jae.container.api import manager

LOG=logging.getLogger(__name__)

CONF = cfg.CONF

class Controller(Base):
    def __init__(self):
        self._manager=manager.Manager()
        #self.db_api = db.API()
        self.mercurial = MercurialControl()

    def index(self,request):
	"""
        return containers list.
	"""
	return webob.exc.HTTPMethodNotAllowed()
	"""
	host = CONF.my_ip
	if not host:
	    return []
	return self.db_api.gets_by_host(host)
	"""

    def show(self,request,id):
	"""
	show info for given container id.
	"""
	return webob.exc.HTTPMethodNotAllowed()

    def delete(self,request,id):
	"""
	delete container for given container id.
	"""
        query = self.db_api.get_container(id)
	if len(query) == 0:
	    LOG.error("no such container")
	    return webob.exc.HttpNotFound()

        eventlet.spawn_n(self._manager.delete,id)

        return Response(200) 

    def create(self,request,body):
	"""create new container and start it."""

	id	   = body.get('db_id')
	name       = body.get('name')
	image_id   = body.get('image_id')
	query = self.db.get_image(image_id)
	if not query:
	    msg = "image id is invalid"
	    raise exception.ImageNotFound(msg) 
	image_uuid = query.uuid
	repository = query.name
	tag	   = queyr.tag

        env        = body.get('env')
        project_id = body.get('project_id') 
        repos      = body.get('repos') 
        branch     = body.get('branch')
        app_type   = body.get('app_type')
        user_id    = body.get('user_id')
        user_key   = body.get('user_key')
	fixed_ip   = body.get('fixed_ip')

	eventlet.spawn_n(self._manager.create,	
			 id,
			 name,
			 image_id,
		 	 image_uuid,
			 repository,
			 tag,
			 repos,
			 branch,
			 app_type,
			 env,
			 user_key,
			 fixed_ip,
			 user_id)	
	return Response(201) 

    def start(self,request,id):
	"""
	start container for given id.
	"""
	id = body.get('id')
        query = self.db_api.get_container(id)
	self.db_api.update_container(
		id = query.id,
		status = "starting")

	bindings = {}
	querys = self.db_api.get_networks(id)
	for query in querys:
		_port = "{}/tcp".format(query.public_port)
		data = {
			_port:
			[
			    {
				"HostIp":query,
				"HostPort":query,
			    }
			]
		}
		bindings.update(data)
	kwargs={
		'Cmd':["/usr/bin/supervisord"],
		'PortBindings':bindings,
	}	
	eventlet.spawn_n(self.con_api.run,
			 kwargs,
			 id,
			 uuid)

        return {"status":200} 

    def stop(self,request,id):
	"""
	stop a container by a given id.
	"""
	eventlet.spawn_n(self._manager.stop,id)

        return Response(204) 

    def reboot(self,request):
	pass

    def destroy(self,request,name):
	"""
	destroy a temporary container by a given name.
	"""
        eventlet.spawn_n(self._manager.destroy,name)

        return {"status":200} 

    def commit(self,request,body):
	repo = body.get('repo') 
	tag = body.get('tag')
	eentlet.spawn_n(self.con_api.commit(repo,tag))

        return {"status":200} 
	
   
    def get_container_info(self,name):
        result=self.compute_api.inspect_container(name)
        container_id = result.json()['Id'][:12]
        network_settings = result.json()['NetworkSettings']
        ports=network_settings['Ports'] 
        private_host = network_settings['IPAddress']
        network_config=list()
        for port in ports:
            private_port = port.rsplit('/')[0] 
            for item in ports[port]:
                host_ip=item['HostIp']
                host_port=item['HostPort']
            network_config.append("{}:{}->{}".format(host_ip,host_port,private_port))
        return (container_id,network_config,)
    
    

 
def create_resource():
    return wsgi.Resource(Controller())
