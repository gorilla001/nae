import webob.exc
import uuid
import eventlet
import os
import requests
import copy
import json

from jae import wsgi
from jae import base
from jae.common import log as logging
from jae.common.mercu import MercurialControl
from jae.common import utils
from jae.common.response import Response, ResponseObject
from jae.image import manager
from jae.image import driver
from jae.common import cfg


CONF=cfg.CONF
LOG=logging.getLogger(__name__)


class Controller(base.Base):
    def __init__(self):
	super(Controller,self).__init__()

        #self.mercurial=MercurialControl()
        #self.driver=driver.API()
        self._manager = manager.Manager()

    def index(self,request):
        return webob.exc.HTTPMethodNotAllowed()

    def show(self,request,id):
        return webob.exc.HTTPMethodNotAllowed()
	
    def create(self,request,body):
        """create image."""
        name       = body.get('name')
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

        eventlet.spawn_n(self._manager.create,
                         id,
                         name,
                         desc,
                         repos,
                         branch,
                         user_id) 

        return Response(201)

    def delete(self,request,id):
	"""
        Delete image by id.
        
        :param request: `wsgi.Request` object
        :param id     : image id
        """
	
	eventlet.spawn_n(self._manager.delete,id)

	return Response(200)

	    
    def edit(self,request,id):
        """edit image online.
        this method is not very correct,change this if you can."""

        http_host=request.environ['HTTP_HOST'].rpartition(":")[0]
	name = utils.random_str()
	port = utils.random_port()
        image_instance = self.db.get_image(id)
        if image_instance:
            image_uuid = image_instance.uuid
            kwargs = {"Image":image_uuid}
            """this method should not be ina greenthread cause 
               it is beatter to prepare edit before client to 
               connect.
            TODO: change this if you can.
            
            eventlet.spawn_n(self._manager.edit,
                             kwargs,
                             http_host,
                             name,
                             port) 
            """
            self._manager.edit(kwargs,
                               http_host,
                               name,
                               port) 

        response = {"url":"http://%s:%s" % \
                   (http_host,port),
                   "name": name}
        return ResponseObject(response) 

    def commit(self,request,body):
        repository = body.get('repository')
        tag = body.get('tag')
        image_id = body.get('id')
        project_id = body.get('project_id') 
        container_name = body.get('container_name')

        project = self.db.get_project(project_id)
        if not project:
            LOG.error("no such project %s" % project_id)
            return Response(404)

        image_instance = self.db.get_image(image_id)
        if image_instance:
            new_image_id = uuid.uuid4().hex
            self.db.add_image(dict(
                             id=new_image_id,
                             name=repository,
                             tag=tag,
                             desc=image_instance.desc,
                             project=copy.deepcopy(project),
                             repos = image_instance.repos,
                             branch = image_instance.branch,
                             user_id = image_instance.user_id,
                             status = 'building'))
            eventlet.spawn_n(self._manager.commit,
                         new_image_id,
                         repository,
                         tag,
                         container_name)

    def destroy(self,request,id):
        """destroy temporary container for image edit."""
        eventlet.spawn_n(self._manager.destroy,id)
      
        return Response(200)
	 
def create_resource():
    return wsgi.Resource(Controller())
