import logging
from nae import db
from nae import image
from nae import utils
from webob import Response



LOG = logging.getLogger('eventlet.wsgi.server')

class API():
    def __init__(self):
        self.url = "http://{}:{}".format(config.docker_host,config.docker_port) 
        self.headers={'Content-Type':'application/json'}
        self.db_api=db.API()
	self.image_api=image.API()

    #@staticmethod
    #def make_request(method,url,headers=self.headers,data=None):
    #    if method == "GET":
    #        rs=requests.get(url,headers=headers)    
    #    if method == "POST":
    #        rs=requests.post(url,data=data,headers=headers)
    #    if method == "DELETE":
    #        rs=requests.delete(url,headers=headers)    

    #    return rs

    #def get_containers(self):
    #    _url="{}/containers/json?all=0".format(self.url)
    #    rs=self.make_request("GET",_url)
    #    return rs

    #def get_container_by_id(self,container_id):
    #    result=requests.get("{}/containers/json?all=1".format(self.url))    
    #    response=webob.Response()
    #    for res in result.json():
    #        if container_id in res['Id']:
    #            pass
    #    return response
    #def create(self,kargs,name,repo_path,user_name,_ctn_id):
    def create(self,kargs,*args):
        data = {
            'Hostname' : '',
            'User'     : '',
            'Memory'   : '',
            'MemorySwap' : '',
            'AttachStdin' : False,
            'AttachStdout' : False,
            'AttachStderr': False,
            'PortSpecs' : [],
            'Tty'   : True,
            'OpenStdin' : True,
            'StdinOnce' : False,
	    'Env':[],
            'Cmd' : [], 
            'Dns' : None,
            'Image' : None,
            'Volumes' : {},
            'VolumesFrom' : '',
            'ExposedPorts': {}
            
        }
        data.update(kargs)
        #eventlet.spawn_n(self._create_container,data,name,_ctn_id,repo_path,user_name)
        utils.execute(self.create_container,data,*args)

    def delete(self,_ctn_id,ctn_id,v):
	status = self.db_api.get_container_status(_ctn_id)
	if status != 'stop':
            self.db_api.update_container_status(
                    id = _ctn_id,
                    status = "stoping"
            )
	    _url="{}/containers/{}/stop?t=10".format(self.url,ctn_id)
	    result=self.make_request("POST",_url)
            if result.status_code == 204:
                self.db_api.update_container_status(
            			id = _ctn_id,
            			status = "stop"
            	)
                self.db_api.update_container_status(
                    	id = _ctn_id,
                    	status = "deleting"
            	)
		_url="{}/containers/{}?v={}".format(self.url,ctn_id,v)
		result=self.make_request("DELETE",_url)
                if result.status_code == 204:
            	    self.db_api.delete_container(_ctn_id)
            if result.status_code == 304:
	        _url="{}/containers/{}?v={}".format(self.url,ctn_id,v)
                self.make_request("DELETE",_url)    
            	self.db_api.delete_container(_ctn_id)
            if result.status_code == 404: 
            	self.db_api.delete_container(_ctn_id)
	else:
		self.db_api.update_container_status(
                    	id = _ctn_id,
                    	status = "deleting"
            	)
		_url="{}/containers/{}?v={}".format(self.url,ctn_id,v)
		result=self.make_request("DELETE",_url)
                if result.status_code == 204:
            	    self.db_api.delete_container(_ctn_id)
		
	return Response(status=200) 

    def start(self,kargs,container_id):
        data = {
            'Binds':[],
            'Links':[],
            'LxcConf':{},
            'PortBindings':{},
            'PublishAllPorts':True,
            'Privileged':False,
            'Dns':[],
            'VolumesFrom':[],
            'CapAdd':[],
            'CapDrop':[],
	    }
        data.update(kargs)
        utils.execute(self.start_container,container_id,data)

	return Response(status=200)

    def stop(self,_ctn_id,ctn_id):
        utils.execute(self.stop_container,_ctn_id,ctn_id)

        return Response(status=200)

    def inspect(self,container_id):
	_url="{}/containers/{}/json".format(self.url,container_id)
	rs=self.make_request("GET",_url)
        return rs

    def run(self,kwargs,_ctn_id,ctn_id):
	data = {
            'Binds':[],
            'Links':[],
            'LxcConf':{},
            'PortBindings':{},
            'PublishAllPorts':False,
            'Privileged':False,
            'Dns':[],
            'VolumesFrom':[],
            'CapAdd':[],
            'CapDrop':[],
	    }
        data.update(kwargs)
        _url="{}/containers/{}/start".format(self.url,ctn_id)
	rs=self.make_request("POST",_url,data=json.dumps(data))
        if rs.status_code == 204:
            self.db_api.update_container_status(
        			id = _ctn_id,
        			status = "ok"
        	)
        return Response(status=200)

    def destroy(self,name):
	utils.execute(self.destroy_container,name)
        return Response(status=200)

    def commit(self,repo,tag):
        utils.execute(self._commit,repo,tag)
        return webob.Response(status=200)

    @staticmethod
    def create_container(data,name,_id,repo_path,user_name):
        _url = "{}/containers/create?name={}".format(self.url,name)
	resp=self.make_request(_url,data=json.dumps(data))
        if resp.status_code == 201:
            container_info = resp.json()
            container_id = container_info["Id"]
            self.db_api.update_container(
            		id = _id,
            		container_id = container_id, 
            		status = 'created'
            		)
            repo_name = os.path.basename(repo_path)	
            path=os.path.join(os.path.dirname(__file__),'files')
            source_path = os.path.join(path,user_name,repo_name)
            dest_path = "/mnt"
            kargs = {
              	'Binds':['{}:{}'.format(source_path,dest_path)],
            	'Dns':[config.DNS.strip("'")],
            }
            self.start_container(kargs,container_id)

        
    
    @staticmethod
    def start_container(container_id,data):
        _url="{}/containers/{}/start".format(self.url,container_id)
	result=self.make_request("POST",_url,data=json.dumps(data))
        if result.status_code == 204:
            self.db_api.update_container_status(
        			id = self._id,
        			status = "ok"
        	)
            result=self.inspect_container(container_id)
            network_settings = result.json()['NetworkSettings']
            ports=network_settings['Ports']
            private_host = network_settings['IPAddress']
            for port in ports:
            		private_port = port.rsplit('/')[0]
            		for item in ports[port]:
                		host_ip=item['HostIp']
                		host_port=item['HostPort']
                        self.db_api.add_network(
                            container_id = container_id,
                            pub_host = host_ip,
                            pub_port = host_port,
                            pri_host = private_host,
                            pri_port = private_port,
                        )
        if result.status_code == 500:
            self.db_api.update_container_status(
        			id = self._id,
        			status = "500"
        ) 

    
    @staticmethod
    def stop_container(_ctn_id,ctn_id):
	_url="{}/containers/{}/stop?t=10".format(self.url,ctn_id)
	result=self.make_reqeust("POST",_url)
	if result.status_code == 204:
            self.db_api.update_container_status(
        			id = _ctn_id,
        			status = "stop"
        	)

    
   
    @staticmethod
    def commit_container(self,repo,tag):
        rs=self.inspect_container('forimageedit')
        if rs.status_code == 200:
            data=rs.json()['Config']
       	    _url="{}/commit?author=&comment=&container=forimageedit&repo={}&tag={}".format(self.url,repo,tag)
       	    result=requests.post(_url,data=json.dumps(data),headers=self.headers)  
            if result.status_code == 201:
		pass

    
    		
    def destroy_container(self,name):
	self.make_request("POST",
			"{}/containers/{}/stop?t=10".format(self.url,name))
	self.make_request("DELETE",
        		"{}/containers/{}?v=1".format(self.url,name))    


