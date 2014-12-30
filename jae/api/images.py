import webob
import uuid
import requests
import json
#from requests.exceptions import ConnectionError, ConnectTimeout, MissingSchema, InvalidSchema
from requests import exceptions
from sqlalchemy.exc import IntegrityError

from jae import wsgi
from jae import image
from jae.base import Base
from jae.common.timeutils import isotime
from jae.common import log as logging
from jae.common import cfg
from jae.common import quotas
from jae.common.exception import BodyEmptyError, ParamNoneError
from jae.common.response import Response, ResponseObject
from jae.common.view import View
from jae.common import utils


CONF=cfg.CONF
LOG=logging.getLogger(__name__)

QUOTAS=quotas.Quotas()

_IMAGE_LIMIT = 12

class Controller(Base):
    def __init__(self):
	super(Controller,self).__init__()

    def index(self,request):
        images=[]
        project_id=request.GET.get('project_id')
        if not project_id:
            LOG.error("project_id cannot be None")
            return Response(404)
        project_instance = self.db.get_project(project_id)
        if project_instance  is None:
            LOG.error("no such project %s" % project_id)
            return Response(404)  
        for image_instance in project_instance.images:
            image={'id':image_instance.id,
                   'uuid':image_instance.uuid,
                   'name':image_instance.name,
		   'tag':image_instance.tag,
                   'desc':image_instance.desc,
                   'project_id':image_instance.project_id,
                   'created':isotime(image_instance.created),
                   'user_id':image_instance.user_id,
                   'status' : image_instance.status}
            images.append(image)

        #query = self.db.get_images(project_id)
        #if query is not None:
        #    for item in query:
        #        image={'id':item.id,
        #               'uuid':item.uuid,
        #               'name':item.name,
	#	       'tag':item.tag,
        #               'desc':item.desc,
        #               'project_id':item.project_id,
        #               'created':isotime(item.created),
        #               'user_id':item.user_id,
        #               'status' : item.status}
        #        images.append(image)
        return ResponseObject(images) 

    def show(self,request,id):
        """get image detail by image `id`"""
	image = {}
        query = self.db.get_image(id)
	if query is not None:
            image = {'id' : query.id,
                     'uuid' : query.uuid,
                     'name' : query.name,
                     'repos' : query.repos,
		     'tag' : query.tag,
                     'desc' : query.desc,
                     'project_id' : query.project_id,
                     'created' : isotime(query.created),
                     'user_id' : query.user_id,
                     'status' : query.status}

        return ResponseObject(image) 

    def create(self,request,body=None):
	if not body:
	    LOG.error('body cannot be empty!')
	    return Response(500) 

        project_id = body.get('project_id')
	if not project_id:
	    LOG.error('project_id cannot be None!')
	    return Response(500) 

	limit = QUOTAS.images or _IMAGE_LIMIT 
	query = self.db.get_images(project_id)
	if len(query) >= limit :
	    LOG.error("images limit exceed,can not created anymore...")
	    return Response(500) 

        name = body.get('name',utils.random_str())
        desc = body.get('desc','')

        repos = body.get('repos')
	if not repos:
	    LOG.error('repos cannot be None!')
	    return Response(500) 

	branch = body.get('branch')
        if not branch:
            LOG.error("branch cannot be None!")
            return Response(500)

        user_id = body.get('user_id')
	if not user_id:
	    LOG.error('user_id cannot be None!')
	    return Response(500) 

	image_service_endpoint = CONF.image_service_endpoint	
	if not image_service_endpoint:
	    LOG.error("image service endpoint not found!")
	    return Response(500)
	try:
            image = requests.post(image_service_endpoint, \
				  headers={'Content-Type':'application/json'}, \
				  data=json.dumps(body))
        except exceptions.ConnectionError:
            LOG.error("Connect to remote server Error")
	    return Response(500) 
	except exceptions.ConnectTimeout:
            LOG.error("Connect to remote server Timeout.")
	    return Response(500) 
        except exceptions.MissingSchema:
            LOG.error("The URL schema (e.g. http or https) is missing.")
	    return Response(500) 
        except exceptions.InvalidSchema:
            LOG.error("The URL schema is invalid.")
	    return Response(500) 

        return ResponseObject(image.json())

    def delete(self,request,id):
 	"""delete image from registry."""
	image_instance = self.db.get_image(id)
	if not image_instance:
	    LOG.warning("no such image %s" % id)
	    return Response(404)
	image_service_endpoint = CONF.image_service_endpoint
	if not image_service_endpoint:
	    LOG.error("no image service endpoint found!")
	    return Response(404)
	if not image_service_endpoint.startswith("http://"):
	    image_service_endpoint += "http://"
	try:
	    response = requests.delete("%s/%s" % \
			(image_service_endpoint,id))
	except ConnectionError,err:
	     LOG.error(err)
	     return Response(500)
	return Response(response.status_code) 

    def edit(self,request,id):
        """edit image online."""
	image_service_endpoint = CONF.image_service_endpoint
	if not image_service_endpoint:
	    LOG.error("no image service endpoint found!")
	    return Response(404)
	if not image_service_endpoint.startswith("http://"):
	    image_service_endpoint += "http://"
        try:
            response=requests.get("%s/%s/edit" % (image_service_endpoint,id))
        except:
            raise
        return ResponseObject(response.json())

    def destroy(self,request,id):
        """destroy temporary containers for image online edit."""
        image_service_endpoint = CONF.image_service_endpoint
	if not image_service_endpoint:
	    LOG.error("no image service endpoint found!")
	    return Response(404)
	if not image_service_endpoint.startswith("http://"):
	    image_service_endpoint += "http://"
        try:
            response=requests.post("%s/%s/destroy" % (image_service_endpoint,id))
        except:
            raise
        return ResponseObject(response.json())

    def commit(self,request):
	repo = request.GET.pop('repo')
	tag = request.GET.pop('tag')
	ctn = request.GET.pop('ctn')
	id = request.GET.pop('id')
 	project_id = request.GET.pop('proj_id')

        limit = QUOTAS.images or _IMAGE_LIMIT 
	query = self.db.get_images(project_id)
	if len(query) >= limit :
	    LOG.error("images limit exceed,can not created anymore...")
	    return Response(500) 

        image_service_endpoint = CONF.image_service_endpoint
	if not image_service_endpoint:
	    LOG.error("no image service endpoint found!")
	    return Response(404)
	if not image_service_endpoint.startswith("http://"):
	    image_service_endpoint += "http://"
        try:
            data = {"repository"     : repo,
                    "tag"            : tag,
                    "container_name" : ctn,
                    "id"             : id,
                    "project_id"     : project_id}
            response=requests.post("%s/commit" % image_service_endpoint,
                                   headers={'Content-Type':'application/json'},
                                   data=json.dumps(data))
        except:
            raise
        return ResponseObject(response.json())

        
	#self.image_api.commit(repo,tag,ctn,id)

    def conflict(self,request):
	_id=request.environ['wsgiorg.routing_args'][1]['image_id']
	ctn_info=self.db.get_containers_by_image(_id)
	ctn_list=[]
	for item in ctn_info.fetchall():
		ctn_name=item[2]
		owner=item[10]
		ctn = {
			"Name":ctn_name,
			"Owner":owner,
		}
		ctn_list.append(ctn)
	LOG.debug(ctn_list)
	return ctn_list

    def baseimage(self,request):
        base_image_list=[]
        image_instances = self.db.get_base_images()
        for instance in image_instances:
             image = {"id":instance.id,
                      "repository": instance.repository,
                      "tag": instance.tag}
             base_image_list.append(image)
        return ResponseObject(base_image_list)
                       
	
def create_resource():
    return wsgi.Resource(Controller())
