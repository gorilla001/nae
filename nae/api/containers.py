import webob.exc
from nae import wsgi
from nae import container,image
from nae import db
from nae.common.mercu import MercurialControl
from nae.common import log as logging

LOG=logging.getLogger(__name__)

class Controller(object):
    def __init__(self):
        self.con_api=container.API()
        self.image_api=image.API()
        self.db_api = db.API()
        self.mercurial = MercurialControl()

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
                    'id':item.prefix,
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
        return containers

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

        return container

    def inspect(self,request):
        container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        result=requests.get("http://0.0.0.0:2375/containers/{}/json".format(container_id))
        return result

    def delete(self,request,body):
        id=body.get('id')
        query = self.db_api.get_container(id)
        eventlet.spawn_n(self.con_api.delete,
			 query.id,
			 query.uuid)

        return {"status":200} 

    def create(self,request,body):
	image_id=body.get('image_id')
	if image == "-1":
	    LOG.error("image can not be empity!")
	    return
        env = body.get('env')
        project_id = body.get('project_id') 
        repos = body.get('repos') 
        branch = body.get('branch')
        app_type= body.get('app_type')
        user_id = body.get('user_id')
        user_key = body.get('user_key')

	ctn_limit = quotas.get_quotas().get('container_limit')	
	ctn_count = self.db_api.get_containers(project_id,user_name)
	ctn_count = len(ctn_count.fetchall())	
	LOG.info(ctn_count)
	if ctn_count == ctn_limit :
	    LOG.warning("containers limit exceed,can not created anymore...")
	    return {"status":100}

        name = os.path.basename(repos) + '-' + branch 
        max_id = self.db_api.get_max_container_id()
        max_id = max_id.fetchone()[0]
        if max_id is not None:
            max_id = max_id + 1;
        else:
            max_id = 0;
        name = name + '-' + str(max_id).zfill(4)
        id = self.db_api.add_container(
                name=name,
                env=env,
                project_id=project_id,
                repos=repos,
                branch=branch,
		image_id=image_id,
                user_id=user_id,
                status="building")

        self.prepare_create(user_id,
			   user_key,
			   repos,
			   branch,
			   env)
        self._create(id,
	             name,
		     image_id,
                     repos,
                     branch,
                     app_type,
                     env,
		     user_key,
		     user_id)
            
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
	eventlet.spawn_n(self.con_api.run,
			 kwargs,
			 id,
			 uuid)

        return {"status":200} 

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
