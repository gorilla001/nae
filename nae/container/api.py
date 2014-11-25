from nae.common import log as logging
from nae import db
from nae import image
from nae.common import utils
from webob import Response
#from nae import driver 
from nae.container import manager
import eventlet



LOG = logging.getLogger(__name__)

class API():
    def __init__(self):
        self.db_api=db.API()
	self.image_api=image.API()
	self._manager = manager.Manager()

    def start(self,kargs,id):
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

    def stop(self,id,uuid):
        utils.execute(self.stop_container,id,uuid)

        return Response(status=200)

    def create(self,body):
	"""
	create a container.
	"""
	eventlet.spawn_n(self._manager.create,body)	
	
    #def create(self,
    #           kargs,
    #           id,
    #           name,
    #           repos,
    #           user_id):
    #    data = {
    #        'Hostname' : '',
    #        'User'     : '',
    #        'Memory'   : '',
    #        'MemorySwap' : '',
    #        'AttachStdin' : False,
    #        'AttachStdout' : False,
    #        'AttachStderr': False,
    #        'PortSpecs' : [],
    #        'Tty'   : True,
    #        'OpenStdin' : True,
    #        'StdinOnce' : False,
    #        'Env':[],
    #        'Cmd' : [], 
    #        'Dns' : None,
    #        'Image' : None,
    #        'Volumes' : {},
    #        'VolumesFrom' : '',
    #        'ExposedPorts': {}
    #        
    #    }
    #    data.update(kargs)
    #    eventlet.spawn_n(self._create,
    #    		 data,
    #                     id,
    #                     name,
    #    		 repos,
    #                     user_id)

    def delete(self,id,uuid):
	status = self.db_api.get_container_status(_ctn_id)
	if status != 'stop':
            self.db_api.update_container(
                    id = id,
                    status = "stoping")
            resp = driver.stop_container(ctn_id)
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

    def run(self,kwargs,id,uuid):
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
        resp = docker.start_container(uuid,data=json.dumps(data))
        if resp.status_code == 204:
            self.db_api.update_container(id = id,status = "ok")

        return Response(status=200)

    
    def inspect(self,id):
        return docker.inspect_container(id) 

    
    def destroy(self,name):
	utils.execute(self.destroy_container,name)
        return Response(status=200)

    def commit(self,repo,tag):
        utils.execute(self._commit,repo,tag)
        return Response(status=200)

    @staticmethod
    def _create(data,
                id,
                name,
                repos,
                user_id):
        resp = driver.container.create(name,
				       data=json.dumps(data))
        if resp.status_code == 201:
            uuid = resp.json()['Id']
            self.db_api.update_container(id= id,
					 uuid= uuid,
            		                 status= 'created' )
            repo_name = os.path.basename(repos)	
            path=os.path.join(os.path.dirname(__file__),'files')
            source_path = os.path.join(path,user_name,repo_name)
            dest_path = "/mnt"
            kargs = {
              	'Binds':['{}:{}'.format(source_path,dest_path)],
            	'Dns':[config.DNS.strip("'")],
            }
            self._start(kargs,id,uuid)

    @staticmethod
    def _start(data,id,uuid):
        resp = driver.container.start(uuid,
                                      data=json.dumps(data))
        if resp.status == 204:
            self.db_api.update_container(id=id,
        			         status='ok')
            resp=self.inspect_container(uuid)
            network_settings = resp.json()['NetworkSettings']
            ports=network_settings['Ports']
            private_host = network_settings['IPAddress']
            for port in ports:
            		private_port = port.rsplit('/')[0]
            		for item in ports[port]:
                		host_ip=item['HostIp']
                		host_port=item['HostPort']
                        self.db_api.add_network(
                             public_host=host_ip,
                             public_port=host_port,
                             private_host=private_host,
                             private_port=private_port,
                             container_id=id)
        if resp.status == 500:
            self.db_api.update_container(id=id,
        			         status=500)
    
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


