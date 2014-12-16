import webob.exc
import os 

from jae.common import cfg
from jae.common import log as logging
from jae.common.cfg import Int, Str
from jae.common import utils
from jae.common.mercu import MercurialControl 

from jae.container import driver
from jae import db
from jae.network import manager


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Manager(object):
    def __init__(self):
	self.db = db.API()
	self.driver = driver.API()
	self.mercurial = MercurialControl()
	self.network = manager.NetworkManager()

    
    def prepare_start(self,
		      user,
                      key,
                      repos,
                      branch):
	"""pull or clone code from repos repos and update to branch branch."""
        user_home=utils.make_user_home(user,key)
        repo_name=os.path.basename(repos)
        if utils.repo_exist(user,repo_name):
            self.mercurial.pull(user,repos)
        else:
            self.mercurial.clone(user,repos)
        self.mercurial.update(user,repos,branch)

    def create(self,
                id,
		name,
		image_id,
		image_uuid,
		repository,
		tag,
		repos,
		branch,
		app_type,
		app_env,
		ssh_key,
		fixed_ip,
		user_id):
	"""create new container use mount of args."""

	resp = self.driver.inspect_image(image_uuid)
	if resp.status_code == 404:
	    LOG.error("inspect error,no such image?")
	    LOG.info("pull image %s from registry..." % image_id)
	    status = self.driver.pull_image(repository,tag)
	    if status == 404:
		LOG.error("pull failed,no registry found!")
	        return webob.exc.HTTPNotFound()
	    if status == 500:
		LOG.error("pull failed,internal server error!")
		return webob.exc.HTTPInternalServerError()
	    LOG.info("pull image succeed!")

	    """check image again.if failed again,what can I do ???"""
	    resp = self.driver.inspect_image(image_uuid)

        port=resp.json()['Config']['ExposedPorts']
	kwargs = {'Hostname'       : '',
                  'User'           : '',
                  'Memory'         : '',
                  'MemorySwap'     : '',
                  'AttachStdin'    : False,
                  'AttachStdout'   : False,
                  'AttachStderr'   : False,
                  'PortSpecs'      : [],
                  'Tty'            : True,
                  'OpenStdin'      : True,
                  'StdinOnce'      : False,
		  'Env'            : ["REPO_PATH=%s" % repos,
			              "BRANCH=%s" % branch,
	                              "APP_TYPE=%s" % app_type,
	                              "APP_ENV=%s" % app_env,
                                      "SSH_KEY=%s" % ssh_key],
            	  'Cmd'            : ["/opt/start.sh"], 
                  'Dns'            : None,
	          'Image'          : image_uuid,
                  'Volumes'        : {},
                  'VolumesFrom'    : '',
                  'ExposedPorts'   : port}

	"""create container."""
	resp = self.driver.create(name,kwargs)
	if resp.status_code == 201:
	    uuid = resp.json()['Id'] 
	    self.db.update_container(id,uuid=uuid,status="created")

	    repo_name = os.path.basename(repos)
            path=os.path.join(os.path.dirname(__file__),'files')
            source_path = os.path.join(path,user_id,repo_name)
            dest_path = "/mnt"
            kwargs = {
                'Binds':['%s:%s' % (source_path,dest_path)],
                'Dns':[CONF.dns],
		'PublishAllPorts':True,
		'PortBindings':{ "22/tcp": [{ "HostIp": fixed_ip }] }
            }

	    """
	    prepare to start container.
	    """
	    self.prepare_start(user_id,ssh_key,repos,branch)

	    """
	    start container and update db status.
	    """
	    status = self.driver.start(uuid,kwargs)
	    if status == 204:
		self.db.update_container(id,status="running")
	    if status == 500:
		LOG.error("start container %s error" % uuid)
		self.db.update_container(id,status="error")
	if resp.status_code == 500:
	    self.db.update_container(id,status='error')
	    raise web.exc.HTTPInternalServerError()
	if resp.status_code == 404:
	    LOG.error("no such image %s" % image_uuid)
	    return

    def delete(self,id):
	query = self.db_api.get(id)
	if query.status == 'running':
	    self.db.update_container(id,status="stoping")
	    status = self.driver.stop(query.uuid)
	    if status in (204,304,404):
		self.db.update_container(id,status="deleting")
		status = self.driver.delete(query.uuid)
		if status in (204,404):
		    self.db.delete(id)
	    if status == 500:
		LOG.error("I donot known what to do")
		return 
	if query.status == 'error':
	    self.db.update_container(id,status="deleting")
	    status = self.driver.delete(query.uuid)
	    if status in (204,404):
		self.db.delete(id)
	if query.status == "stoped":
	    status = self.driver.delete(query.uuid)
	    if status in (204,404):
		self.db.delete(id)

    def start(self,kwargs,uuid):
	return status

    def stop(self,id):
	"""
	stop container for a given id.
	"""
	query = self.db.get(id)
	if query.status == "stoped":
	    return
	self.db.update_container(id,status="stoping") 
	status = self.driver.stop(query.uuid)
	if status == 204:
	    self.db.update_container(id,status="stoped")
    
    def destroy(self,name):
	"""
	destroy a temporary container by a given name.
	"""
	self.driver.stop(name)
	self.driver.delete(name)
