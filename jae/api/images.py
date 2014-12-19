import webob
import uuid
import requests
import json
from requests import ConnectionError
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
        query = self.db.get_images(project_id)
        if query is not None:
            for item in query:
                image={'id':item.id,
                       'uuid':item.uuid,
                       'name':item.name,
		       'tag':item.tag,
                       'desc':item.desc,
                       'project_id':item.project_id,
                       'created':isotime(item.created),
                       'user_id':item.user_id,
                       'status' : item.status}
                images.append(image)
        return ResponseObject(images) 

    def show(self,request,id):
	image = {}
        query = self.db.get_image(id)
	if query is not None:
            image = {'id' : query.id,
                     'uuid' : query.uuid,
                     'name' : query.name,
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

        name = body.get('name') or utils.random_str()
        desc = body.get('desc') or ''

        repos = body.get('repos')
	if not repos:
	    LOG.error('repos cannot be None!')
	    return Response(500) 

	branch = body.get('branch') or 'default'

        user_id = body.get('user_id')
	if not user_id:
	    LOG.error('user_id cannot be None!')
	    return Response(500) 

	image_service_endpoint = CONF.image_service_endpoint	
	if not image_service_endpoint:
	    LOG.error("image service endpoint not found!")
	    return Response(500)
	try:
	    print image_service_endpoint
            image = requests.post(image_service_endpoint, \
				     headers={'Content-Type':'application/json'}, \
				     data=json.dumps(body))
	except:
	    pass
        return ResponseObject(image.json())

    def delete(self,request,id):
 	"""delete image (id)."""
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
        query = self.db.get_image(id)
	name = utils.random_str()
	port = utils.random_port()
	kwargs={"Image":query.uuid}
	self.image_api.edit(kwargs,name,port)
	
	return {
		"url":"http://{}:{}".format(config.docker_host,port),
		"name":name,
		}

    def commit(self,request):
	repo = request.GET.pop('repo')
	tag = request.GET.pop('tag')
	ctn = request.GET.pop('ctn')
	id = request.GET.pop('id')
 	proj_id = request.GET.pop('proj_id')

	img_limit = quotas.get_quotas().get('image_limit')	
	img_count = self.db.get_images(proj_id)
	img_count = len(img_count.fetchall())	
	if img_count == img_limit :
	    LOG.info("images limit exceed,can not created anymore...")
	    return { "status":100 }

	self.image_api.commit(repo,tag,ctn,id)

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
	
def create_resource():
    return wsgi.Resource(Controller())
