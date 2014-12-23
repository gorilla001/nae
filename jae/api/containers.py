import webob.exc
import requests

from jae import wsgi
from jae.common import log as logging
from jae.common.exception import ContainerLimitExceeded
from jae.common.response import Response, ResponseObject
from jae.common import quotas
from jae.common import cfg
from jae.common import timeutils
from jae.scheduler import scheduler
from jae.base import Base

CONF=cfg.CONF

LOG=logging.getLogger(__name__)

QUOTAS=quotas.Quotas()

class Controller(Base):
    def __init__(self):
	super(Controller,self).__init__()

	if not CONF.default_scheduler:
	    self._scheduler=scheduler.SimpleScheduler()

    def index(self,request):
	"""
        return containers list.
	"""
        containers=[]

        project_id = request.GET.get('project_id')
        user_id = request.GET.get('user_id')
        
        query = self.db.get_containers(project_id,user_id)
        for item in query:
            container = {
                    'id':item.id,
                    'name':item.name,
		    'network':item.fixed_ip,
                    'created':timeutils.isotime(item.created),
                    'status':item.status,
                    }
            containers.append(container)
        return ResponseObject(containers)

    def show(self,request,id):
	container={}
        query= self.db.get_container(id)
        if query is not None:
            container = {
                'id':query.id,
                'name':query.name,
		'uuid':query.uuid,
                'env':query.env,
                'project_id':query.project_id,
                'repos':query.repos,
                'branch':query.branch,
                'image_id':query.image_id,
                'network':query.fixed_ip,
                'created':timeutils.isotime(query.created),
                'user_id':query.user_id,
		'host_id':query.host_id,
                'status':query.status,
                }

        return ResponseObject(container)

    
    def create(self,request,body=None):
	if not body:
	    msg = "post request has no body?"
	    LOG.error(msg)
	    return webob.exc.HTTPBadRequest(explanation=msg)
	project_id = body.get('project_id')
	if not project_id:
	    msg = "project id must be provided."
	    LOG.error(msg)
	    return webob.exc.HTTPBadRequest(explanation=msg)

	image_id = body.get('image_id')
	if image_id == "-1":
	    msg = "invalid image id -1."
	    LOG.error(msg)
	    return web.exc.HttpBadRequest(explanation=msg)
        query = self.db.get_image(image_id)
        if not query: 
	    msg = "image id is invalid,no such image."
            LOG.error(msg)
            return webob.exc.HTTPBadRequest(explanation=msg)

	user_id = body.get('user_id')
	if not user_id:
	    msg = "user id must be provided."
	    LOG.error(msg)
	    return webob.exc.HTTPBadRequest(explanation=msg)

	limit = QUOTAS.containers or _CONTAINER_LIMIT
	query = self.db.get_containers(project_id,user_id)
	if len(query) >= limit:
	    msg = 'container limit exceeded!!!'
	    LOG.error(msg)
	    return webob.exc.HTTPForbidden(explanation=msg)

	repos = body.get('repos')
	if not repos:
	    msg = "repos must be provided"
	    LOG.error(msg)
	    return webob.exc.HTTPBadRequest(explanaiton=msg)

	branch = body.get('branch')
	if not branch:
	    msg = "branch must be provided"
	    LOG.error(msg)
	    return webob.exc.HTTPBadRequest(explanaiton=msg)

	env = body.get('env')
	if not env:
	    msg = "env must be provided"
	    LOG.error(msg)
	    return webob.exc.HTTPBadRequest(explanation=msg)

	user_key = body.get('user_key','')

        zone_id = body.get('zone_id',0)
	
	try:
	    instance = self._scheduler.run_instance(project_id,
						    user_id,
						    image_id,
						    repos,
						    branch,
						    env,
						    user_key,
                                                    zone_id)
	except:
	    raise 
	    
	return ResponseObject(instance)

    def delete(self,request,id):
        container = self.db.get_container(id)
	if not container:
	    return Response(200)
	host_id = container.host_id
	host = self.db.get_host(host_id)	
	if not host:
	    LOG.error("no such host %s" % host_id)
	    return Response(404)

	host,port = host.host,host.port
	response = requests.delete("http://%s:%s/v1/containers/%s" \
			%(host,port,id))
        return Response(response.status_code) 

    def start(self,request,id):
	container = self.db.get_container(id)
	if not container:
	    LOG.error("nu such container %s" % id)
	    return Response(404)
	host = self.db.get_host(container.host_id)
	if not host:
	    LOG.error("no such host")
	    return Response(404)
	host,port = host.host,host.port
	response=requests.post("http://%s:%s/v1/containers/%s/start" \
		      % (host,port,id))

	return Response(response.status_code)

    def stop(self,request,id):
	"""send stop request to remote host where container on."""
        container = self.db.get_container(id)
	if not container:
	    LOG.error("nu such container %s" % id)
	    return Response(404)

	host_id = container.host_id
	host = self.db.get_host(host_id)
	if not host:
	    LOG.error("no such host")
	    return Response(404)

	host,port = host.host,host.port 
	response = requests.post("http://%s:%s/v1/containers/%s/stop" \
		      % (host,port,id))

        return Response(response.status_code) 

    def reboot(self,request):
	pass

    def destroy(self,request,body):
	"""send destroy request to remote host."""
 	id=body.get('id')	
        eventlet.spawn_n(self.con_api.destroy(id))

        return Response(200) 

    def commit(self,request,body):
	"""send commit request to remote host."""
	repo = body.get('repo') 
	tag = body.get('tag')
	eventlet.spawn_n(self.con_api.commit(repo,tag))

        return Response(200) 

    def refresh(self,request,id):
        """refresh code in container."""
        container = self.db.get_container(id)
	if not container:
	    LOG.error("nu such container %s" % id)
	    return Response(404)
        
	host_id = container.host_id
	host = self.db.get_host(host_id)
	if not host:
	    LOG.error("no such host")
	    return Response(404)
	
	host,port = host.host,host.port 
	response = requests.post("http://%s:%s/v1/containers/%s/refresh" \
		      % (host,port,id))

        return Response(response.status_code) 
 
def create_resource():
    return wsgi.Resource(Controller())
