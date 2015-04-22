import webob.exc
import requests
from jsonschema import SchemaError, ValidationError

from nae import wsgi
from nae.common import log as logging
from nae.common.exception import ContainerLimitExceeded
from nae.common.response import Response, ResponseObject
from nae.common import quotas
from nae.common import cfg
from nae.common import timeutils
from nae.scheduler import scheduler
from nae.common import exception
from nae.common import client
from nae.base import Base

CONF=cfg.CONF

LOG=logging.getLogger(__name__)

QUOTAS=quotas.Quotas()

EMPTY_STRING=""

class Controller(Base):
    def __init__(self):
	super(Controller,self).__init__()

	if not CONF.default_scheduler:
	    self._scheduler=scheduler.SimpleScheduler()

        self.http=client.HTTPClient()

    def index(self,request):
	"""
        List all containers on all container nodes according to `project_id`
        and `user_id`.
        
        This method returns a dictionary list and each dict contains the following keys:
            - id 
            - name 
            - repos
            - branch
            - image
            - network
            - created
            - status

        If no container found, empty list will be returned.
	"""
        containers = []

        project_id = request.GET.get('project_id')
        user_id = request.GET.get('user_id')
        
        query = self.db.get_containers(project_id,user_id)
        for item in query:
            container = {
                'id': item.id,
                'name': item.name,
                'repos': item.repos,
                'branch': item.branch,
                'image_id': item.image_id,
	        'network': item.fixed_ip,
                'created': timeutils.isotime(item.created),
                'status': item.status,
                }
            container.setdefault("image","")
            """Get the image name and tag by the `image_id`.
               if the image not found, use the default."""
            image_id = item.image_id
            image_instance = self.db.get_image(image_id)
            if image_instance:
                image = "%s:%s" % (image_instance.name,image_instance.tag)
                container.update({"image":image})

            containers.append(container)
        return ResponseObject(containers)

    def show(self,request,id):
        """
        Show the container info according by container's id `id`.

        This method returns a dictionary with following keys:
            - id
            - name
            - uuid
            - env
            - project_id
            - repos
            - branch
            - image_id
            - network
            - created
            - user_id
            - host_id
            - status
         
        If no container found, empty dictionary will returned.
        """

	container={}
        query= self.db.get_container(id)
        if query is not None:
            container = {
                'id': query.id,
                'name': query.name,
		'uuid': query.uuid,
                'env': query.env,
                'project_id': query.project_id,
                'repos': query.repos,
                'branch': query.branch,
                'image_id': query.image_id,
                'network': query.fixed_ip,
                'created': timeutils.isotime(query.created),
                'user_id': query.user_id,
		'host_id': query.host_id,
                'status': query.status,
                }

        return ResponseObject(container)

    
    def create(self,request,body=None):
        """
        For creating container, body should not be None and
        should contains the following params:
            - project_id  the project's id which the containers belong to
            - image_id    the image's id which used for creation 
            - user_id     the user which the container belong to
            - repos       the repos which will be tested  
            - branch      the branch which will be tested 
            - env         the envrionment which the container belong to(eg.DEV/QA/STAG/PUB/PROD)
            - user_key    the user's public key which will be inject to container
            - zone_id     the zone's id which the container belong to(eg.BJ/CD)
        All the above parmas are not optional and have no default value.
        """
        """This schema is used for data validate."""
        schema = {
            "type": "object",
            "properties": {
                "project_id": {
                     "type": "string",
                     "minLength": 32,
                     "maxLength": 64,
                     "pattern": "^[a-zA-Z0-9]*$",
                },
                "image_id": {
                     "type": "string",
                     "minLength": 32,
                     "maxLength": 64,
                     "pattern": "^[a-zA-Z0-9]*$",
                },
                "user_id": {
                    "type": "string",
                    "minLength": 32,
                    "maxLength": 64,
                    "pattern": "^[a-zA-Z0-9]*$",
                },
                "repos": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255,
                },
                "branch": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255,
                },
                "env": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255,
                },
                "user_key": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255,
                },
                "zone_id": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255,
                },
            },       
            "required": [ "project_id","image_id","user_id","repos","branch","env","user_key","zone_id" ] 
        }
        
        try:
            self.validator(body,schema)
        except (SchemaError,ValidationError) as ex:
            LOG.error(ex) 
	    return webob.exc.HTTPBadRequest(explanation="Bad Paramaters")

        """Limit check"""
        limit = QUOTAS.containers or _CONTAINER_LIMIT
	query = self.db.get_containers(project_id,user_id)
	if len(query) >= limit:
	    msg = 'container limit exceeded!!!'
	    LOG.error(msg)
	    return webob.exc.HTTPForbidden(explanation=msg)

        """Call the scheduler to decide which host the container will 
           be run on.
        """
        # TODO(nmg): This should be modified to use rpc call not function call. 
	try:
	    instance = self._scheduler.run_instance(project_id,
						    user_id,
						    image_id,
						    repos,
						    branch,
						    env,
						    user_key,
                                                    zone_id)
	except exception.NoValidHost:
	    raise 
	    
	return ResponseObject(instance)

    def delete(self,request,id):
        """
        Send delete `request` to container node for deleting.
        if failed,excepiton will be occured.

        This method contains the following two steps:
            - find the host where the container run on
            - send delete request to that host
        If no host found, the request will be droped.

        :param request: `wsgi.Request`
        :param id     : container idenfier
        """ 
        container = self.db.get_container(id)
	if not container:
	    return webob.exc.HTTPOk() 

	host_id = container.host_id
	host = self.db.get_host(host_id)	
	if not host:
	    LOG.error("no such host %s" % host_id)
	    return webob.exc.HTTPNotFound() 

	host,port = host.host,host.port
        # FIXME: try to catch exceptions and dealing with it. 
	response = self.http.delete("http://%s:%s/v1/containers/%s" \
			%(host,port,id))
        return Response(response.status_code) 

    def start(self,request,id):
        """
        Send start `request` to container node for starting container. 

        This method contains the following two steps:
            - find the host where the container run on
            - send start request to that host
        If no host was found, the request will be droped.

        :params request: `wsgi.Request`
        :params id     : container id
        """
	container = self.db.get_container(id)
	if not container:
	    LOG.error("nu such container %s" % id)
	    return webob.exc.HTTPNotFound() 
	host = self.db.get_host(container.host_id)
	if not host:
	    LOG.error("no such host")
	    return webob.exc.HTTPNotFound() 
	host,port = host.host,host.port
        
        response=self.http.post("http://%s:%s/v1/containers/%s/start" \
                       %(host,port,id))

	return Response(response.status_code)

    def stop(self,request,id):
	"""
        Send stop `request` to container node for stoping container.

        This method contains the following two steps:
            - find the host where the container run on
            - send stop request to that host
        If no host found, the request will be droped.
        
        :params request: `wsgi.Request`
        :params id     : container id
        """ 
        container = self.db.get_container(id)
	if not container:
	    LOG.error("nu such container %s" % id)
	    return webob.exc.HTTPNotFound() 

	host_id = container.host_id
	host = self.db.get_host(host_id)
	if not host:
	    LOG.error("no such host")
	    return webob.exc.HTTPNotFound() 

	host,port = host.host,host.port 
	response = self.http.post("http://%s:%s/v1/containers/%s/stop" \
		      % (host,port,id))

        return Response(response.status_code) 

    def reboot(self,request,id):
        """Reboot the specified container.""" 
        return NotImplementedError()

    def destroy(self,request,body):
	"""Send destroy request to remote host."""

        return NotImplementedError()

    def commit(self,request,body):
	"""Send commit request to container node."""

        return NotImplementedError() 

    def refresh(self,request,id):
        """
        Refresh code in container. `refresh request` will be 
        send to remote container server for refreshing.
        if send request failed,exception will occured.
        Is it necessary to catch the exception? I don't
        know. 

        :param request: `wsgi.Request` object
        :param id     : container idenfier
        """
        """
        Check if this container is really exists,
        otherwise return 404 not found.
        """
        container = self.db.get_container(id)
	if not container:
	    LOG.error("nu such container %s" % id)
	    return webob.exc.HTTPNotFound() 
        
        """
        Get host id from container info,
        if host id is None,return 404.
        """
	host_id = container.host_id
        if not host_id:
            LOG.error("container %s has no host_id" % id)
	    return webob.exc.HTTPNotFound() 
        
        """
        Get host instance by `host_id`,
        if host instance is None,return 404.
        """
	host = self.db.get_host(host_id)
	if not host:
	    LOG.error("no such host")
	    return webob.exc.HTTPNotFound() 

        """Get ip address and port for host instance."""	
	host,port = host.host,host.port 
          
        """send `refresh request` to the host where container on."""
        #FIXME: exception shoud be catched?
	response = self.http.post("http://%s:%s/v1/containers/%s/refresh" \
		      % (host,port,id))

        return Response(response.status_code) 
 
def create_resource():
    return wsgi.Resource(Controller())
