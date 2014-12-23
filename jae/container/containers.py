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
from jae.container import manager
from jae.common import states

LOG=logging.getLogger(__name__)

CONF = cfg.CONF

class Controller(Base):
    def __init__(self):
	super(Controller,self).__init__()

        self._manager=manager.Manager()
        self.mercurial = MercurialControl()

    def index(self,request):
	"""
        return containers list.
	"""
	return webob.exc.HTTPMethodNotAllowed()

    def show(self,request,id):
	"""
	show info for given container id.
	"""
	return webob.exc.HTTPMethodNotAllowed()

    def delete(self,request,id):
	"""
	delete container for given container id.
	"""
        query = self.db.get_container(id)
	if not query:
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
	tag	   = query.tag

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
        query = self.db.get_container(id)
        if query.status == states.RUNNING:
            LOG.info("already running,ignore...")
            return Response(204)
        eventlet.spawn_n(self._manager.start,id)

        return Response(204)

    def stop(self,request,id):
	"""
	stop a container by a given id.
	"""
	query = self.db.get_container(id)
        if query.status == states.STOPED:
            LOG.info("already stoped,ignore...")
            return Response(204)
	eventlet.spawn_n(self._manager.stop,id)

        return Response(204) 

    def reboot(self,request,id):
	"""reboot a container""" 
        return NotImplemented	

    def destroy(self,request,name):
	"""
	destroy a temporary container by a given name.
	"""
        eventlet.spawn_n(self._manager.destroy,name)

        return {"status":200} 

    def commit(self,request,body):
	repo = body.get('repo') 
	tag = body.get('tag')
	eventlet.spawn_n(self.con_api.commit(repo,tag))

        return Response(200) 
    
    def refresh(self,id):
        """refresh code in container."""
        query = self.db.get_container(id)
        if not query:
            LOG.info("container %s not found" % id)
            return Response(404)
        eventlet.spawn(self._manager.refresh,id)  
        
        return Response(204)
        
	
   
def create_resource():
    return wsgi.Resource(Controller())
