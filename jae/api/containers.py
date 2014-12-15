import webob.exc
from jae import wsgi
from jae.api import container,image
from jae.common import log as logging
from jae.common.view import View
from jae.common.exception import ContainerLimitExceeded
from jae.common.response import Response, ResponseObject
from jae.common import quotas
from jae.scheduler import scheduler
from jae.base import Base

LOG=logging.getLogger(__name__)

QUOTAS=quotas.Quotas()

class Controller(Base):
    def __init__(self):
	if not CONF.default_scheduler:
	    self._scheduler=scheduler.SimpleScheduler()

    def index(self,request):
	"""
        return containers list.
	"""
        containers=[]

        project_id = request.GET.get('project_id')
        user_id = request.GET.get('user_id')
        
        query = self.db_api.get_containers(project_id,user_id)
        for item in query:
            container = {
                    'id':item.id,
                    'name':item.name,
		    'network':[],
                    'created':item.created,
                    'status':item.status,
                    }
	    """
            container_id = item.prefix
            query = self.db_api.get_networks(container_id)
            if query is not None:	
                networks = [] 
                for net in query:
                    pub_host = net.public_host
                    pub_port = net.public_port
                    pri_port = net.private_port
                    network_config ="{}:{}~{}".format(pub_host,pub_port,pri_port)
                    networks.append(network_config)
                data = {
                "network":networks,
                }
                container.update(data)
	    """
            containers.append(container)
        return View(containers)

    def show(self,request,id):
	container={}
        query= self.db_api.get_container(id)
        if query is not None:
            container = {
                'name':query.name,
                'id':query.prefix,
                'env':query.env,
                'project_id':query.project_id,
                'repos':query.repos,
                'branch':query.branch,
                'image':query.image,
                'network':query.network,
                'created':query.created,
                'user_id':query.user_id,
                'status':query.status,
                }

        return View(container)

    def delete(self,request,id):
        query = self.db_api.get_container(id)
        eventlet.spawn_n(self.con_api.delete,
			 query.id,
			 query.uuid)

        return Response(200) 

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
	if image == "-1":
	    msg = "invalid image id -1."
	    LOG.error(msg)
	    return web.exc.HttpBadRequest(explanation=msg)
        #query = self.db_api.get_image(image_id)
        #if not query: 
	#    msg = "image id is invalid,no such image."
        #    LOG.error(msg)
        #    return webob.exc.HTTPBadRequest(explanation=msg)
	"""
	"""get image repository for image pull if necessary"""
	image_repository = query.name 

	"""get image tag for image pull if necessary""" 
	image_tag = query.tag

	"""image uuid for container creation"""
	image_uuid = query.uuid
	"""
	user_id = body.get('user_id')
	if not user_id:
	    msg = "user id must be provided."
	    LOG.error(msg)
	    return webob.exc.HTTPBadRequest(explanation=msg)

	limit = QUOTAS.containers or _CONTAINER_LIMIT
	query = self.db_api.get_containers(project_id,user_id)
	if len(query) >= limit:
	    #raise ContainerLimitExceeded()  
	    msg = 'container limit exceeded!!!'
	    LOG.error(msg)
	    return webob.exc.HTTPForbidden(explanation=msg)

	repos = body.get('repos')
	if not repos:
	    msg = "repos must be provided"
	    LOG.error(msg)
	    return webob.exc.HTTPBadRequest(explanaiton=msg)

	branch = body.get('branch') or 'default'

	env = body.get('env') or 'QA'

	user_key = body.get('user_key') or ''
	
	#eventlet.spawn_n(self._manager.create,body)
	try:
	    instance = self._scheduler.run_instance(project_id,
						    user_id,
						    image_id,
						    repos,
						    branch,
						    env,
						    user_key,
						     )
	except:
	    pass
	    
	return ResponseObject(instance)

    def start(self,request,body):
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
	#eventlet.spawn_n(self.con_api.run,
	#		 kwargs,
	#		 id,
	#		 uuid)
		
        return self._start(host,port,id) 
    def _start(self,host,port,id):
	resp = requests.post("http://%s:%s/containers/%s/start" % (host,port,id))
	return resp.status_code

    def stop(self,request,body):
        id=body.get('id')
        query = self.db_api.get_container(id)
	self.db_api.update_container(
		id = query.id,
		status = "stoping")
	eventlet.spawn_n(self.con_api.stop,
			query.id,
			query.uuid)

        return {"status":200} 

    def reboot(self,request):
	pass

    def destroy(self,request,body):
 	id=body.get('id')	
        eventlet.spawn_n(self.con_api.destroy(id))

        return {"status":200} 

    def commit(self,request,body):
	repo = body.get('repo') 
	tag = body.get('tag')
	eentlet.spawn_n(self.con_api.commit(repo,tag))

        return {"status":200} 
	
    def _create(self,
                id,
		name,
		image_id,
		repos,
		branch,
		app_type,
		app_env,
		ssh_key,
		user_id):
        query = self.db_api.get_image(image_id)
	if len(query) == 0:
	    LOG.error("image can not be empity!")
	    return 
        resp = self.image_api.inspect_image(query.uuid)
        port=resp.json()['Config']['ExposedPorts']
        kwargs={
                'Image':query.uuid,
	    'Env':[
	          "REPO_PATH={}".format(repos),
	          "BRANCH={}".format(branch),
	          "APP_TYPE={}".format(app_type),
	          "APP_ENV={}".format(app_env),
                  "SSH_KEY={}".format(ssh_key),
	    	],
            	'Cmd' : ["/opt/start.sh"], 
                'ExposedPorts':port,
	    
            }
        self.con_api.create(kwargs,
			   id,
			   name,
			   repos,
			   user_id)
    @staticmethod
    def prepare_create(user,key,hg,branch,env):
        user_home=utils.make_user_home(user,key)
        repo_name=os.path.basename(hg)
        if utils.repo_exist(user,repo_name):
            self.mercurial.pull(user,hg)
        else:
            self.mercurial.clone(user,hg)
        self.mercurial.update(user,hg,branch)

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
