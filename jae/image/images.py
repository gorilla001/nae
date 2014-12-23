import webob.exc
import uuid
import eventlet
import os
import requests
import copy
import json

from jae import wsgi
from jae import base
from jae.common import log as logging
from jae.common.mercu import MercurialControl
from jae.common import utils
from jae.common.response import Response, ResponseObject
from jae.image import driver
from jae.common import cfg


CONF=cfg.CONF
LOG=logging.getLogger(__name__)


class Controller(base.Base):
    def __init__(self):
	super(Controller,self).__init__()

        self.mercurial=MercurialControl()
        self.driver=driver.API()

    def index(self,request):
        return webob.exc.HTTPMethodNotAllowed()

    def show(self,request,id):
        return webob.exc.HTTPMethodNotAllowed()
	
    def create(self,request,body):
        """create image."""
        name       = body.get('name')
        desc       = body.get('desc')
        project_id = body.get('project_id')
        repos      = body.get('repos')
        branch     = body.get('branch')
        user_id    = body.get('user_id')
        id         = uuid.uuid4().hex

        project = self.db.get_project(project_id)
        if not project:
            LOG.error("no such project %s" % project_id)
            return Response(404)

        """add db entry first."""
        self.db.add_image(dict(
                id=id,
                name=name,
                tag="latest",
                desc=desc,
                project=copy.deepcopy(project),
                repos = repos,
                branch = branch,
                user_id = user_id,
                status = 'building'))
        """create image ina greenthread."""
        eventlet.spawn_n(self._create,
                         id,
                         name,
                         repos,
                         branch,
                         user_id)

        """retrun the created image id."""
        return ResponseObject({"id":id}) 

    def _create(self,
		id,
                name,
                repos,
                branch,
                user_id):
        """create container."""
        repo_name=os.path.basename(repos)
	user_home = os.path.join("/home",user_id)
	if not os.path.exists(user_home):
	    os.mkdir(user_home)
        if utils.repo_exist(user_id,repo_name):
	    try:
                self.mercurial.pull(user_id,repos)
	    except:
                LOG.error("pull %s failed!" % repos)
                self.db.update_image(id,status="error")
                raise
        else:
	    try:
                self.mercurial.clone(user_id,repos)
	    except:
                LOG.error("clone %s failed!" % repos)
                self.db.update_image(id,status="error")
                raise
        self.mercurial.update(user_id,repos,branch)
        tar_path=utils.make_zip_tar(os.path.join(user_home,repo_name))

	with open(tar_path,'rb') as data:
	    LOG.info("BUILD +job build %s" % name)
	    status=self.driver.build(name,data)
        if status == 404:
	    LOG.error("request URL not Found!")
	    LOG.info("BUILD -job build %s = ERR" % name)
            return 
	if status == 200:
	    LOG.info("BUILD -job build %s = OK" % name)
	    """update db entry if successful build."""
            status,json=self.driver.inspect(name)
	    uuid = json.get('Id')
            self.db.update_image(id,uuid=uuid)
	    """ tag image into repositories if successful build."""
	    LOG.info("TAG +job tag %s" % id)
	    tag_status,tag =self.driver.tag(name)
	    LOG.info("TAG -job tag %s" % id)
	    if tag_status == 201:
		"""push image into repositories if successful tag."""
		LOG.info("PUSH +job push %s" % tag)
		push_status=self.driver.push(tag)
		if push_status == 200:
		    LOG.info("PUSH -job push %s = OK" % tag)
		    """update db entry if successful push."""
                    self.db.update_image(id,status="ok")
		else:
                    self.db.update_image(id,status="error")
		    LOG.info("PUSH -job push %s = ERR" % tag)
        if status == 500:
	    self.db.update_image(id,status = "error")
	    LOG.error("image {} create failed!".format(name)) 
	    LOG.info("BUILD -job build %s = ERR" % name)

    def delete(self,request,id):
	"""
        Delete image by id.
        
        :param request: `wsgi.Request` object
        :param id     : image id
        """
	
	eventlet.spawn_n(self._delete,id)

	return Response(200)

    def _delete(self,id):
	LOG.info("DELETE +job delete %s" % id)
	image_instance = self.db.get_image(id)
	if image_instance:
	    repository = image_instance.name
	    tag = image_instance.tag
	    self.db.update_image(id,
		       status="deleting")
	    status = self.driver.delete(repository,tag)
	    if status in (200,404):
	        self.db.delete_image(id)
	    if status in (409,500):
	        self.db.update_image(id,status=status)
	LOG.info("DELETE -job delete %s" % id)
    
    def edit(self,request,id):
        http_host=request.environ['HTTP_HOST'].rpartition(":")[0]
	name = utils.random_str()
	port = utils.random_port()
        image_instance = self.db.get_image(id)
        if image_instance:
            image_uuid = image_instance.uuid
            kwargs = {"Image":image_uuid}
            eventlet.spawn_n(self._edit,kwargs,http_host,name,port) 

        response = {"url":"http://%s:%s" % \
                   (http_host,port),
                   "name": name}
        return ResponseObject(response) 

    def _edit(self,kwargs,host,name,port):
	 data = {'Hostname' : '',
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
                 'ExposedPorts': {"17698/tcp": {}}}

         data.update(kwargs)
         resp = requests.post("http://%s:%s/containers/create?name=%s" % \
                            (CONF.host,CONF.port,name),
                            headers={'Content-Type':'application/json'},
                            data=json.dumps(data))
         if resp.status_code == 201:
             data = {'Binds':[],
                    'Links':[],
                    'LxcConf':{},
                    'PublishAllPorts':False,
                    'PortBindings':{"17698/tcp":[{"HostIp":host,"HostPort":str(port)}]},
                    'Cmd':["/opt/webssh/term.js/example/index.js"],
                    'Privileged':False,
                    'Dns':[],
                    'VolumesFrom':[],
                    'CapAdd':[],
                    'CapDrop':[]}
             container_uuid = resp.json()['Id']
             resp = requests.post("http://%s:%s/containers/%s/start" % \
                                 (CONF.host,CONF.port,container_uuid),
                                 headers={'Content-Type':'application/json'},
                                 data=json.dumps(data))
             if resp.status_code != 204:
                 LOG.debug("start for-image-edit container failed")
         else:
	     LOG.debug("create for-image-edit container failed") 

def create_resource():
    return wsgi.Resource(Controller())
