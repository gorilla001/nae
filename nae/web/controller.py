import webob.exc
import uuid
import eventlet
import os
import requests
import copy
import json

from nae import wsgi
from nae import base
from nae.common import log as logging
from nae.common.mercu import MercurialControl
from nae.common import utils
from nae.common.response import Response, ResponseObject
from nae.image import manager
from nae.image import driver
from nae.common import cfg


CONF=cfg.CONF
LOG=logging.getLogger(__name__)


class Controller(base.Base):
    def __init__(self):
	super(Controller,self).__init__()

        self._manager = manager.Manager()

    def index(self,request):
        return webob.exc.HTTPMethodNotAllowed()

    def show(self,request,id):
        return webob.exc.HTTPMethodNotAllowed()
	
    def create(self,request,body):
        """create image."""
        name       = body.get('name').lower()
        desc       = body.get('desc')
        project_id = body.get('project_id')
        repos      = body.get('repos')
        branch     = body.get('branch')
        user_id    = body.get('user_id')
        id         = uuid.uuid4().hex

        project = self.db.get_project(project_id)
        if not project:
            LOG.error("no such project %s" % project_id)
            return Response(404)

        """add db entry first."""
        self.db.add_image(dict(
                id=id,
                name=name,
                tag="latest",
                desc=desc,
                repos = repos,
                branch = branch,
                user_id = user_id,
                status = 'building'),
                project = project)

        #eventlet.spawn_n(self._manager.create,
        #                 id,
        #                 name,
        #                 desc,
        #                 repos,
        #                 branch,
        #                 user_id) 

        self._process_task(self._manager.create,
                           id,
                           name,
                           desc,
                           repos,
                           branch,
                           user_id) 
        return ResponseObject({"id":id})

    def delete(self,request,id):
	"""
        Delete image by id.
        
        :param request: `wsgi.Request` object
        :param id     : image id
        """
	
	#eventlet.spawn_n(self._manager.delete,id)
	self._process_task(self._manager.delete,id)
       

	return Response(200)

	    
    def edit(self,request,id):
        """edit image online.
        this method is not very correct,change this if you can."""

        """if HTTP_HOST is localhost,this will be failed,so use
        CONF.host instead.
        http_host=request.environ['HTTP_HOST'].rpartition(":")[0]
        """
        http_host=CONF.host
	name = utils.random_str()
	port = 17698 
        image_instance = self.db.get_image(id)
        if image_instance:
            image_uuid = image_instance.uuid
            kwargs = {"Image":image_uuid}
            """this method should not be ina greenthread cause 
               it is beatter to prepare edit before client to 
               connect.
            TODO: change this if you can.
            
            self._manager.edit(kwargs,
                               http_host,
                               name,
                               port) 
            """
            #eventlet.spawn_n(self._manager.edit,
            #                 kwargs,
            #                 http_host,
            #                 name,
            #                 port) 

            self._process_task(self._manager.edit,
                               kwargs,
                               http_host,
                               name,
                               port) 
        response = {"url":"http://%s:%s" % \
                   (http_host,port),
                   "name": name}
        return ResponseObject(response) 

    def commit(self,request,body):
        """
        Commit specified container to named image.
        if image repository is provided, use the provided repository
        as the new image's repository, otherwise get the image name
        by `image_id` for the repoistory.
        """ 
        repository   = body.pop('repository')
        tag          = body.pop('tag')
        image_id     = body.pop('id')
        project_id   = body.pop('project_id') 
        container_id = body.pop('container_id')

        project = self.db.get_project(project_id)
        if not project:
            LOG.error("no such project %s" % project_id)
            return Response(404)

        container_instance=self.db.get_container(container_id)
        if not container_instance:
            LOG.error("no such container %s" % container_id)
            return Response(404)
        container_uuid = container_instance.uuid

        image_instance = self.db.get_image(image_id)
        if not image_instance:
            LOG.error("no such image %s" % image_id)
            return Response(404)

        """If repository is None, use the image's name as repository."""
        if not repository:
            repository = image_instance.name

        new_image_id = uuid.uuid4().hex
        self.db.add_image(dict(
                         id=new_image_id,
                         name=repository,
                         tag=tag,
                         desc=image_instance.desc,
                         repos = image_instance.repos,
                         branch = image_instance.branch,
                         user_id = image_instance.user_id,
                         status = 'building'),
                         project=project)
        #eventlet.spawn_n(self._manager.commit,
        #             new_image_id,
        #             repository,
        #             tag,
        #             container_uuid)

        self._process_task(self._manager.commit,
                           new_image_id,
                           repository,
                           tag,
                           container_uuid)
        #NOTE(nmg):there may be a bug here.
        return ResponseObject({"id":new_image_id})

    def destroy(self,request,id):
        """destroy temporary container for image edit."""
        #eventlet.spawn_n(self._manager.destroy,id)
        self._process_task(self._manager.destroy,id)
      
        return Response(200)
    def _process_task(self,func,*args):
       """Generate a greenthread to run the `func` with the `args`""" 
       self.run_task(func,*args)

def create_resource():
    return wsgi.Resource(Controller())
