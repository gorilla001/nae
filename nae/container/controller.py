import logging

LOG=logging.getLogger('eventlet.wsgi.server')

class ContainerController(object):
    def __init__(self):
        self.compute_api=ContainerAPI()
        self.image_api=ImageAPI()
        self.db_api = DBAPI()
        self.mercurial = MercurialControl()

    @webob.dec.wsgify
    def __call__(self,request):
        method=request.environ['wsgiorg.routing_args'][1]['action']
        method=getattr(self,method)     
        response=webob.Response()
        result_json=method(request)
        response.headers.add("Content-Type","application/json")
        response.json=result_json
        return response

    def index(self,request):
        project_id = request.GET.get('project_id')
        user_id = request.GET.get('user_id')

        rs = self.db_api.get_containers(project_id,user_id)
        container_list = list()
        for item in rs.fetchall():
            container = {
                    'ID':item[0],
                    'Name':item[2],
		            #'AccessMethod':'  '.join(ast.literal_eval(item[7])),
		            'AccessMethod':'',
                    'Created':item[9],
                    'Status':item[11],
                    }
            container_id = item[1]
            network_info = self.db_api.get_network(container_id)
            network_list = list()
            for net in network_info.fetchall():
                pub_host = net[2]
                pub_port = net[3]
                pri_port = net[5]
                network_config ="{}:{}~{}".format(pub_host,pub_port,pri_port)
                network_list.append(network_config)
            data = {
                "AccessMethod":'  '.join(network_list),
            }
            container.update(data)
            container_list.append(container)
        return container_list

    def show(self,request):
        container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        container_info = self.db_api.get_container(container_id).fetchone()
        project_info=self.db_api.get_project(container_info[4]).fetchone()
        container = {
                'name':container_info[2],
                'id':container_info[1],
                'env':container_info[3],
                'project':project_info[1],
                'hgs':container_info[5],
                'code':container_info[6],
                'access':' '.join(ast.literal_eval(container_info[7])),
                'created':container_info[8],
                'createdby':container_info[9],
                'status':container_info[10],
                }
        return container

    def inspect(self,request):
        container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        result=requests.get("http://0.0.0.0:2375/containers/{}/json".format(container_id))
        return result

    def delete(self,request):
        result_json={"status":"200"}
        _container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        _v = request.GET.get('v')
        container_info = self.db_api.get_container(_container_id).fetchone()
        container_id = container_info[1]
        eventlet.spawn_n(self.compute_api.delete_container,_container_id,container_id,_v)
        return result_json

    def create(self,request):
        container_image=request.json.pop('container_image')
	if container_image == "-1":
	    LOG.error("image can not be empity!")
	    return
        container_env = request.json.pop('container_environ')
        project_id = request.json.pop('container_project')
        container_hg=request.json.pop('container_hg')
        container_code = request.json.pop('container_code')
        app_type= request.json.pop('app_type')
        user_name = request.json.pop('user_name')
        user_key = request.json.pop('user_key')

	ctn_limit = quotas.get_quotas().get('container_limit')	
	ctn_count = self.db_api.get_containers(project_id,user_name)
	ctn_count = len(ctn_count.fetchall())	
	LOG.info(ctn_count)
	if ctn_count == ctn_limit :
	    LOG.warning("containers limit exceed,can not created anymore...")
	    return {"status":100}

        container_name = os.path.basename(container_hg) + '-' + container_code 
        max_id = self.db_api.get_max_container_id()
        max_id = max_id.fetchone()[0]
        if max_id is not None:
            max_id = max_id + 1;
        else:
            max_id = 0;
        container_name = container_name + '-' + str(max_id).zfill(4)
        created_time = utils.human_readable_time(time.time())
        _container_id = self.db_api.add_container(
                container_name=container_name,
                container_env=container_env,
                project_id=project_id,
                container_hg=container_hg,
                container_code=container_code,
		container_image=container_image,
                created=created_time,
                created_by=user_name,
                status="building")

        self.prepare_start_container(user_name,user_key,container_hg,container_code,container_env)
        self.start_container(container_name,container_image,container_hg,container_code,app_type,container_env,user_key,user_name,_container_id)

    def stop(self,request):
        _ctn_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        _ctn_info = self.db_api.get_container(_ctn_id).fetchone()
        ctn_id = _ctn_info[1]
	self.db_api.update_container_status(
		id = _ctn_id,
		status = "stoping",
	)
	eventlet.spawn_n(self.compute_api.stop_container,_ctn_id,ctn_id)
        
    def start(self,request):
	_ctn_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        _ctn_info = self.db_api.get_container(_ctn_id).fetchone()
        ctn_id = _ctn_info[1]
	self.db_api.update_container_status(
		id = _ctn_id,
		status = "starting",
	)

	bindings = {}
	network_info=self.db_api.get_network(ctn_id)
	for _net in network_info.fetchall():
		_port = "{}/tcp".format(_net[5])
		data = {
			_port:
			[
			    {
				"HostIp":_net[2],
				"HostPort":_net[3],
			    }
			]
		}
		bindings.update(data)
	kwargs={
		'Cmd':["/usr/bin/supervisord"],
		'PortBindings':bindings,
	}	
	eventlet.spawn_n(self.compute_api.start_container_once,kwargs,_ctn_id,ctn_id)

    def reboot(self,request):
	self.stop(request)

    def commit(self,request):
	repo = request.GET.pop('repo')
	tag = request.GET.pop('tag')
	self.compute_api.commit(repo,tag)
	
    def start_container(self,name,image,repo_path,branch,app_type,app_env,ssh_key,user_name,_container_id):
        image_info = self.db_api.get_image(image).fetchone()
	if image_info is None:
	    LOG.error("image can not be empity!")
	    return 
        image_id = image_info[1]
        result=self.image_api.inspect_image(image_id)
        result_json=result.json()
        port=result_json['Config']['ExposedPorts']
        kwargs={
                'Image':image_id,
	    'Env':[
	          "REPO_PATH={}".format(repo_path),
	          "BRANCH={}".format(branch),
	          "APP_TYPE={}".format(app_type),
	          "APP_ENV={}".format(app_env),
                  "SSH_KEY={}".format(ssh_key),
	    	],
            	'Cmd' : ["/opt/start.sh"], 
                'ExposedPorts':port,
	    
            }
        self.compute_api.create_container(kwargs,name,repo_path,user_name,_container_id)

    def prepare_start_container(self,user,key,hg,branch,env):
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
            #network_config.append("{}:{}->{}:{}".format(host_ip,host_port,private_host,private_port))
            network_config.append("{}:{}->{}".format(host_ip,host_port,private_port))
        return (container_id,network_config,)

    def destroy(self,request):
	name=request.environ['wsgiorg.routing_args'][1]['container_id']
        self.compute_api.destroy(name)
 
