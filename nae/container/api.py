import logging
from nae import db
from nae import image
from nae import utils
from webob import Response
from nae import docker



LOG = logging.getLogger('eventlet.wsgi.server')

class API():
    def __init__(self):
        self.db_api=db.API()
	self.image_api=image.API()

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
            res = docker.stop_container(ctn_id)
            if result.status_code == 204:
                self.db_api.update_container_status(
            			id = _ctn_id,
            			status = "stop"
            	)
                self.db_api.update_container_status(
                    	id = _ctn_id,
                    	status = "deleting"
            	)
                res = docker.delete_container(ctn_id,v)
                if res.status_code == 204:
            	    self.db_api.delete_container(_ctn_id)
            if res.status_code == 304:
                docker.delete_container(ctn_id,v)
            	self.db_api.delete_container(_ctn_id)
            if res.status_code == 404: 
            	self.db_api.delete_container(_ctn_id)
	else:
		self.db_api.update_container({
                    	   'id':id,
                    	   'status':"deleting"})
                res = docker.delete_container(ctn_id,v)
                if res.status_code == 204:
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

    def inspect(self,id):
        return docker.inspect_container(id) 

    def run(self,kwargs,id,prefix):
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
        resp = docker.start_container(prefix,data=json.dumps(data))
        if resp.status_code == 204:
            self.db_api.update_container(id = id,status = "ok")

        return Response(status=200)

    def destroy(self,name):
	utils.execute(self.destroy_container,name)
        return Response(status=200)

    def commit(self,repo,tag):
        utils.execute(self._commit,repo,tag)
        return Response(status=200)

    @staticmethod
    def create_container(data,name,id,repo_path,user_name):
        resp = docker.create_container(name,data=json.dumps(data))
        if resp.status_code == 201:
            container_info = resp.json()
            prefix= container_info["Id"][:12]
            self.db_api.update_container(id = id,{ 'prefix' : prefix,
            		                           'status' : 'created'})
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
    def start_container(id,data):
        resp = docker.start_container(id,data=json.dumps(data))
        if resp.status == 204:
            self.db_api.update_container(id=id,
        			         status='ok')
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
                            {'container_id' : container_id,
                             'pub_host' : host_ip,
                             'pub_port' : host_port,
                             'pri_host' : private_host,
                             'pri_port' : private_port})
        if res.status == 500:
            self.db_api.update_container({'id':id,
        			          'status':500})
    
    @staticmethod
    def stop_container(id,prefix):
	resp = docker.stop_container(id)
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
        return docker.destroy_container(name)


