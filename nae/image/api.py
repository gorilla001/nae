from nae.common import log as logging
from nae.common.response import Response
from nae import db
import eventlet
import os
import json
from nae.common import cfg
import requests


CONF=cfg.CONF

LOG=logging.getLogger(__name__)

class API():
    def __init__(self):
        self.db_api=db.API()
    
    def create(self,body):
        eventlet.spawn_n(self._create,
                         json.dumps(body))

        return Response(200)

    def _create(self,body):
        url = CONF.image_service_endpoint 
        if not url:
            LOG.error("image service endpoint must be specfied!")
            return
        requests.post(url,data=body)

    def delete(self,id):
	eventlet.spawn_n(self._delete,id)

	return Response(200)

    def _delete(self,id):
        url = CONF.image_service_endpoint 
        if not url:
            LOG.error("image service endpoint must be specfied!")
            return
	request_url = url + "/" + id
	requests.delete(request_url)
 	
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
