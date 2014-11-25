from utils import MercurialControl
import logging

LOG=logging.getLogger('eventlet.wsgi.server')

class API():
    def __init__(self):
        self.url="http://{}:{}".format(config.docker_host,config.docker_port)
	self.headers = {'Content-Type':'application/json'}	
        self.mercurial = MercurialControl()
        self.db_api=db.API()

    @staticmethod
    def make_request(method,url,headers=self.headers,data=None):
	if method == 'GET':
            res=requests.get(url,headers=headers)  
	if method == 'POST':
	    res=requests.post(url,headers=headers,data=data)
	if method == "DELETE":
	    res=requests.delete(url,headers=headers)
	return res	

    def get_images(self):
	url = "{}/images/json".format(self.url)
	res = self.make_request("GET",url)
        return res

    def inspect_image(self,image_id):
	url = "{}/images/{}/json".format(self.url,image_id)
	res = self.make_request("GET",url)
        return res

    @staticmethod
    def _create_image(url,image_name,tar_path,_id):
	data=open(tar_path,'rb')
        headers={'Content-Type':'application/tar'}
	url="{}/build?t={}".format(url,image_name)
	rs=self.make_request("POST",url,data=data)
	    if rs.status_code == 200:
            	result=self.inspect_image(image_name)
	        if result.status_code == 200:
                    image_size=result['VirtualSize']
            	    image_size = utils.human_readable_size(image_size)
		    image_id=result.json()['Id'][:12]
            	    self.db_api.update_image(
			               id=_id,
                                       image_id=image_id,
                                       size=image_size,
                                       status = "ok")
		if result.status_code == 404:
		    LOG.error("image {} create failed!".format(image_name)) 
		if result.status_code == 500:
			self.db_api.update_image(
				  id=id,
                                  image_id='',
                                  size='',
                                  status = "500")
            if rs.status_code == 500:
	        self.db_api.update_image(
				  id=id,
                                  image_id='',
                                  size='',
                                  status = "500")

    def create_image(self,id,image_name,repo_path,repo_branch,user_name):
        repo_name=os.path.basename(repo_path)
        if utils.repo_exist(user_name,repo_name):
            self.mercurial.pull(user_name,repo_path)
        else:
            self.mercurial.clone(user_name,repo_path)
        self.mercurial.update(user_name,repo_path,repo_branch)
        file_path=utils.get_file_path(user_name,repo_name)
        tar_path=utils.make_zip_tar(file_path)
        eventlet.spawn_n(self._create_image,self.url,image_name,tar_path,id)
        result=webob.Response('{"status_code":200"}')
        return result

    @staticmethod
    def _delete_image(url,image_id,f_id,_id):
	url = "{}/images/{}?force={}".format(self.url,image_id,f_id)
	res = self.make_request("DELETE",url)
	status_code = res.status_code 
	if status_code == 200 or status_code == 404:
	    self.db_api.delete_image(_id)
	if status_code == 409: 
	    if not self.db_api.get_containers_by_image(id).fetchone():	
	        self.db_api.delete_image(_id)	
		return
	    self.db_api.update_image_status(
	                               id=_id,
                                       status = "409")
        if status_code == 500: 
	    self.db_api.update_image_status(
				      id=_id,
                                      status = "500")

    def delete_image(self,id,image_id,f_id):
	eventlet.spawn_n(self._delete_image,image_id,f_id,id)
        result=webob.Response('{"status_code":200"}')
	return result

    @staticmethod
    def _edit(kwargs,name,port):
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
	    'Cmd':["/opt/webssh/term.js/example/index.js"],
            'Dns' : None,
            'Image' : None,
            'Volumes' : {},
            'VolumesFrom' : '',
            'ExposedPorts': {
			"17698/tcp": {},
			}
            
        }
	data.update(kwargs)
	_url="{}/containers/create?name={}".format(self.url,name)
	resp = self.make_request("POST",_url,data=json.dumps(data))
        if resp.status_code == 201:
	    data = {
           	'Binds':[],
            	'Links':[],
            	'LxcConf':{},
            	'PublishAllPorts':False,
		'PortBindings':{ 
			"17698/tcp": [
				{ 
				    "HostIp":config.docker_host,
				    "HostPort":"{}".format(port), 
				}
			] 
		},
		"Cmd":["/opt/webssh/term.js/example/index.js"],
            	'Privileged':False,
            	'Dns':[],
            	'VolumesFrom':[],
            	'CapAdd':[],
            	'CapDrop':[],
	    }
	    ctn_id = resp.json()['Id']
            _url="{}/containers/{}/start".format(self.url,ctn_id)
	    result=self.make_request("POST",_url,data=json.dumps(data))
            if result.status_code != 204:
	        LOG.debug("start for-image-edit container failed")	
	    else:
	        LOG.debug("create for-image-edit container failed") 

    def edit(self,kargs,name,port):
        eventlet.spawn_n(self._edit,kargs,name,port)
        result=webob.Response('{"status_code":200"}')
        return result

    @staticmethod
    def _commit(repo,tag,ctn,id):
	_url="{}/containers/{}/json".format(self.url,ctn)
	rs=self.make_request("GET",_url)
        if rs.status_code == 200:
	    img_info=self.db_api.get_image(id).fetchone()
            created_time = utils.human_readable_time(time.time())
	    _id=self.db_api.add_image(
            	name=repo,
		tag=tag,
                desc=img_info[5],
                project_id=img_info[6],
                repo = img_info[7],
		branch = img_info[8], 
                created= created_time,
                owner=img_info[10],
                status = 'building'
		)
       	    _url="{}/commit?author=&comment=&container={}&repo={}&tag={}".format(self.url,ctn,repo,tag)
            headers={'Content-Type':'application/json'}
            data=rs.json()['Config']
	    result=self.make_request(_url,data=json.dumps(data))
            if result.status_code == 201:
		_img_id=result.json()['Id']	
		_url="{}/images/{}/json".format(self.url,_img_id)
		rs=self.make_request("GET",_url)
		if rs.status_code == 200:
		    size = rs.json()['VirtualSize']
            	    img_size = utils.human_readable_size(size)
		    _url="{}/containers/{}/stop?t=10".format(self.url,ctn)
		    self.make_request("POST",_url)
		    _url="{}/containers/{}?v=1".format(self.url,ctn)
		    self.make_request("DELETE",_url)
		    self.db_api.update_image(
		                       id=_id,
                                       image_id=_img_id,
                                       size=img_size,
                                       status = "ok")

    def commit(self,repo,tag,ctn,id):
        eventlet.spawn_n(self._commit,repo,tag,ctn,id)
        result=webob.Response('{"status_code":200"}')
        return result
