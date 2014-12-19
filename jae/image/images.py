import webob.exc
import uuid
import eventlet
import os
import requests

from jae import wsgi
from jae import db
from jae import base
from jae.common import log as logging
from jae.common.mercu import MercurialControl
from jae.common import utils
from jae.common.response import Response
from jae.image import driver


LOG=logging.getLogger(__name__)


class Controller(base.Base):
    def __init__(self):
	super(Controller,self).__init__()

        self.mercurial=MercurialControl()
        self.driver=driver.API()

    def index(self,request):
        return webob.exc.HTTPMethodNotAllowed()

    def show(self,request,id):
        return webob.exc.HTTPMethodNotAllowed()
	
    def create(self,request,body):
        name       = body.get('name')
        desc       = body.get('desc')
        project_id = body.get('project_id')
        repos      = body.get('repos')
        branch     = body.get('branch')
        user_id    = body.get('user_id')
        id         = uuid.uuid4().hex
        self.db.create(dict(
                id=id,
                name=name,
                tag="latest",
                desc=desc,
                project_id=project_id,
                repos = repos,
                branch = branch,
                user_id = user_id,
                status = 'building'))

        eventlet.spawn_n(self._create,
                         id,
                         name,
                         repos,
                         branch,
                         user_id)


        return Response(200) 

    def _create(self,
		id,
                name,
                repos,
                branch,
                user_id):
        repo_name=os.path.basename(repos)
        if utils.repo_exist(user_id,repo_name):
            self.mercurial.pull(user_id,repos)
        else:
            self.mercurial.clone(user_id,repos)
        self.mercurial.update(user_id,repos,branch)
        file_path=utils.get_file_path(user_id,repo_name)
        tar_path=utils.make_zip_tar(file_path)

	with open(tar_path,'rb') as data:
	    status=self.driver.build(name,data)
        if status == 404:
	    LOG.error("request URL not Found!")
            return 
	if status == 200:
            status,json=self.driver.inspect(name)
	    if status == 200:
		uuid = json.get('Id')
            	self.db.update(id,
                               uuid=uuid,
                               status = "ok")
	    if status == 404:
            	self.db.update(id,
			       status="error")
	        LOG.error("image {} create failed!".format(name)) 
	    if status == 500:
	        self.db.update(id,
                               status = "500")
	        LOG.error("image {} create failed!".format(name)) 
        if status == 500:
	    self.db.update(id,
                           status = "500")
	    LOG.error("image {} create failed!".format(name)) 

    def delete(self,request,id):
	"""delete image by id"""
	
	eventlet.spawn_n(self._delete,id)

	return Response(200)

    def _delete(self,id):
	LOG.info("DELETE +job delete %s" % id)
	image_instance = self.db.get_image(id)
	if not image_instance.uuid:
	    self.db.update_image(id,
		       status="deleting")
	    status = self.driver.delete(image_instance.uuid)
	    if status in (200,404):
	        self.db.delete_image(id)
	    if status in (409,500):
	        self.db.update_image(id,status=status)
	LOG.info("DELETE -job delete %s" % id)
	    
	    
def create_resource():
    return wsgi.Resource(Controller())
