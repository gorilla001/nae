from nae.common.mercu import MercurialControl
from nae.common import log as logging
from nae.common import driver
from nae.common import utils
from nae import db
import eventlet
import os
from webob import Response


LOG=logging.getLogger(__name__)

class API():
    def __init__(self):
        self.mercurial = MercurialControl()
        self.db_api=db.API()
	self.driver=driver.API()
    
    def get_images(self):
	url="{}/images/json".format(self.url)
	return self.request_get(url)

    def inspect_image(self,image_id):
	url = "{}/images/{}/json".format(self.url,image_id)
	return self.request_get(url)

    def _create(self,
		id,
                name,
                repos,
                branch,
                user_id):
        repo_name=os.path.basename(repos)
        if utils.repo_exist(user_id,repo_name):
            self.mercurial.pull(user_id,repos)
        else:
            self.mercurial.clone(user_id,repos)
        self.mercurial.update(user_id,repos,branch)
        file_path=utils.get_file_path(user_id,repo_name)
        tar_path=utils.make_zip_tar(file_path)

	with open(tar_path,'rb') as data:
	    resp=self.driver.image_create(name,data)
	if resp.status_code == 200:
            inspect=self.driver.image_inspect(name)
	    if inspect.status_code == 200:
                size=inspect['VirtualSize']
                size = utils.human_readable_size(size)
		uuid = inspect.json()['Id']
            	self.db_api.update_image(
		               id=id,
                               uuid=uuid,
                               size=size,
                               status = "ok")
	    if inspect.status_code == 404:
            	self.db_api.update_image(
				id=id,
				status="error")
	        LOG.error("image {} create failed!".format(name)) 
	    if inspect.status_code == 500:
	        self.db_api.update_image(
			  id=id,
                          status = "500")
	        LOG.error("image {} create failed!".format(name)) 
        if resp.status_code == 500:
	    self.db_api.update_image(
			  id=id,
                          status = "500")
	    LOG.error("image {} create failed!".format(name)) 

    def create(self,
	       id,
               name,
               repos,
               branch,
               user_id):
        eventlet.spawn_n(self._create,
                         id,
                         name,
                         repos,
                         branch,
                         user_id)

        return Response({"status":200})

        

    @staticmethod
    def _delete_image(url,image_id,f_id,_id):
	url = "{}/images/{}?force={}".format(self.url,image_id,f_id)
	res = self.request_delete(url)
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
        return webob.Response('{"status_code":200"}')

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
	resp = self.request_post(_url,data=json.dumps(data))
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
	    result=self.request_post(_url,data=json.dumps(data))
            if result.status_code != 204:
	        LOG.debug("start for-image-edit container failed")	
	    else:
	        LOG.debug("create for-image-edit container failed") 

    def edit(self,kargs,name,port):
        eventlet.spawn_n(self._edit,kargs,name,port)
        return webob.Response('{"status_code":200"}')

    @staticmethod
    def _commit(repo,tag,ctn,id):
	_url="{}/containers/{}/json".format(self.url,ctn)
	rs=self.request_get(_url)
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
            data=rs.json()['Config']
	    result=self.request_post(_url,data=json.dumps(data))
            if result.status_code == 201:
		_img_id=result.json()['Id']	
		_url="{}/images/{}/json".format(self.url,_img_id)
		rs=self.request_get(_url)
		if rs.status_code == 200:
		    size = rs.json()['VirtualSize']
            	    img_size = utils.human_readable_size(size)
		    _url="{}/containers/{}/stop?t=10".format(self.url,ctn)
		    self.request_post(_url)
		    _url="{}/containers/{}?v=1".format(self.url,ctn)
		    self.request_delete(_url)
		    self.db_api.update_image(
		                       id=_id,
                                       image_id=_img_id,
                                       size=img_size,
                                       status = "ok")

    def commit(self,repo,tag,ctn,id):
        eventlet.spawn_n(self._commit,repo,tag,ctn,id)
        return webob.Response('{"status_code":200"}')
