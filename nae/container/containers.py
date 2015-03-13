import webob.exc
import uuid
import os

from nae import wsgi
from nae.base import Base
from nae.common.mercu import MercurialControl
from nae.common import log as logging
from nae.common.view import View
from nae.common.response import Response
from nae.common import cfg
from nae.container import manager
from nae.common import states

LOG=logging.getLogger(__name__)

CONF = cfg.CONF

class Controller(Base):
    def __init__(self):
	super(Controller,self).__init__()

        self._manager=manager.Manager()

    def index(self,request):
	"""
        Return containers list.
	"""
	return webob.exc.HTTPMethodNotAllowed()

    def show(self,request,id):
	"""
	Show info for given container id.
	"""
	return webob.exc.HTTPMethodNotAllowed()

    def delete(self,request,id):
	"""
	Delete container by container id.
        
        :params request: `wsgi.Request`
        :params id     : container id
	"""
        query = self.db.get_container(id)
	if not query:
	    LOG.error("no such container")
	    return webob.exc.HttpNotFound()

        try:
            self._process_task(self._manager.delete,id)
        except:
            raise

        return Response(200) 

    def create(self,request,body):
	"""Create new container and start it."""
        # FIXME(nmg): try to do this with a pythonic way.

	id	   = body.pop('db_id')
	name       = body.pop('name')
	image_id   = body.pop('image_id')

	query = self.db.get_image(image_id)
	if not query:
	    msg = "image id is invalid"
	    raise exception.ImageNotFound(msg) 

	image_uuid = query.uuid
	repository = query.name
	tag	   = query.tag

        env        = body.pop('env')
        project_id = body.pop('project_id') 
        repos      = body.pop('repos') 
        branch     = body.pop('branch')
        app_type   = body.pop('app_type')
        user_id    = body.pop('user_id')
        user_key   = body.pop('user_key')
	fixed_ip   = body.pop('fixed_ip')

        try:
            self._process_task(self._manager.create,
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
        except:
 	    raise

	return Response(201) 

    def start(self,request,id):
	"""
        Start container according container id. 
      
        :params request: `wsgi.Request`
        :params      id: the container id

        returns: if start succeed, 204 will be returned.
        """
        query = self.db.get_container(id)
        if query.status == states.RUNNING:
            LOG.info("already running,ignore...")
            return Response(204)
        # FIXME(nmg)
        try:
            self._process_task(self._manager.start,id)
        except:
            raise

        return Response(204)

    def stop(self,request,id):
	""" 
        Stop container according container id. 
       
        :params request: `wsgi.Request`
        :params id: the container id

        returns: if stop succeed, 204 will be returned.
	"""
	query = self.db.get_container(id)
        if query.status == states.STOPED:
            LOG.info("already stoped,ignore...")
            return Response(204)
        # FIXME(nmg)
        try:
	    self._process_task(self._manager.stop,id)
        except:
            raise

        return Response(204) 

    def reboot(self,request,id):
	"""Reboot a container""" 
        return NotImplemented	

    def destroy(self,request,name):
	"""
	Destroy a temporary container by a given name.

        :params name: the temporary container name
	"""
        # FIXME(nmg)
        try:
            self._process_task(self._manager.destroy,name)
        except:
            raise

        return Response(200) 

    def commit(self,request,body):
        """Commit container to image."""
        # FIXME(nmg)
	repo = body.pop('repo') 
	tag = body.pop('tag')
        try:
            self._process_task(self._manager.commit(repo,tag))
        except:
            raise

        return Response(200) 
    
    def refresh(self,request,id):
        """Refresh code in container."""
        query = self.db.get_container(id)
        if not query:
            LOG.info("container %s not found" % id)
            return Response(404)
        # FIXME(nmg) 
        try:
            self._process_task(self._manager.refresh,id)
        except:
            raise
        
        return Response(204)

    #@staticmethod
    def _process_task(func,*args):
        """Generate a eventlet greenthread to process the task."""
        # FIXME(nmg)
        self.run_task(func,*args)
   
def create_resource():
    return wsgi.Resource(Controller())
