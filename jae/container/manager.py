import webob.exc
import os 

from jae.common import cfg
from jae.common import log as logging
from jae.common.cfg import Int, Str
from jae.common import utils
from jae.common.mercu import MercurialControl 
from jae.common.exception import NetWorkError
from jae.common import nwutils

from jae.container import driver
from jae import base 
from jae.network import manager


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Manager(base.Base):
    def __init__(self):
	super(Manager,self).__init__()

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
        if utils.repo_exist(user_home,repo_name):
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

	LOG.info("CREATE +job create %s" % id)
	resp = self.driver.inspect_image(image_uuid)
	if resp.status_code == 404:
	    LOG.error("inspect error,no such image?")
	    LOG.info("pull image %s from registry..." % image_id)
	    status = self.driver.pull_image(repository,tag)
	    if status == 404:
		LOG.error("pull failed,no registry found!")
                self.db.update_container(id,
                                         status="error")
	        return webob.exc.HTTPNotFound()
	    if status == 500:
		LOG.error("pull failed,internal server error!")
                self.db.update_container(id,
                                         status="error")
		return webob.exc.HTTPInternalServerError()

	    """check image again.if failed again,what can I do ???"""
	    resp = self.driver.inspect_image(image_uuid)
	    if resp.status_code == 404:
		msg="pull image failed!"
		LOG.error(msg)
		return webob.exc.HTTPNotFound(explanation=msg)
	    LOG.info("pull image succeed!")

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
                  'ExposedPorts'   : port,
		  "RestartPolicy": { "Name": "always" }}

	"""create container."""
	resp = self.driver.create(name,kwargs)
	if resp.status_code == 201:
	    uuid = resp.json()['Id'] 
	    self.db.update_container(id,uuid=uuid,status="created")

	    network = self.network.get_fixed_ip() 
	    try:
	        nwutils.create_virtual_iface(uuid[:8],network)
	    except NetWorkError:
		raise
	    self.db.update_container(id,fixed_ip=network)

            PB={}
	    EP=port
            for key in EP.keys():
                nt_list=[]
                nt = { "HostIp":network,
                       "HostPort":key.rpartition("/")[0]
                     }
                nt_list.append(nt)
                PB[key] = nt_list

	    repo_name = os.path.basename(repos)
            path=os.path.join(CONF.static_file_path,'files')
            source_path = os.path.join(path,user_id,repo_name)
            dest_path = "/mnt"
            kwargs = {
                'Binds':['%s:%s' % (source_path,dest_path)],
                'Dns':[CONF.dns],
		'PublishAllPorts':True,
		'PortBindings':PB
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
        if resp.status_code == 409:
	    self.db.update_container(id,status='error')
            LOG.error("CONFLICT!!!")
            return

	LOG.info("CREATE -job create %s = OK" % id)
    def delete(self,id):
	LOG.info("DELETE +job delete %s" % id)
	query = self.db.get_container(id)
	if query.status == 'running':
	    self.db.update_container(id,status="stoping")
	    status = self.driver.stop(query.uuid)
	    if status in (204,304,404):
		self.db.update_container(id,status="deleting")
		status = self.driver.delete(query.uuid)
		if status in (204,404):
		    self.db.delete_container(id)
	    if status == 500:
		LOG.error("I donot known what to do")
		return 
	elif query.status == 'error':
	    self.db.update_container(id,status="deleting")
	    status = self.driver.delete(query.uuid)
	    if status in (204,404):
		self.db.delete_container(id)
	elif query.status == "stoped":
	    status = self.driver.delete(query.uuid)
	    if status in (204,404):
		self.db.delete_container(id)
	else:
           self.db.update_container(id,status="deleting")
           self.db.delete_container(id)
        try:
            nwutils.delete_virtual_iface(query.uuid[:8])
        except:
            LOG.warning("delete virtual interface error")  

	LOG.info("DELETE -job delete %s" % id)

    def start(self,id):
	"""start container"""
	LOG.info("START +job start %s" % id)
	self.db.update_container(id,status="starting") 
	query = self.db.get_container(id)
	uuid = query.uuid
	network = query.fixed_ip
	image_id = query.image_id
	image = self.db.get_image(image_id)
	resp = self.driver.inspect_image(image.uuid)
        port=resp.json()['Config']['ExposedPorts']
	PB={}
        EP=port
        for key in EP.keys():
            nt_list=[]
            nt = { "HostIp":network,
                   "HostPort":key.rpartition("/")[0]}
            nt_list.append(nt)
            PB[key] = nt_list
	kwargs={"Cmd":["/usr/bin/supervisord"],
		"PortBindings":PB}
	status = self.driver.start(uuid,kwargs)
	if status == 204:
	    self.db.update_container(id,status="running")
	LOG.info("START -job start %s" % id)

    def stop(self,id):
	"""
	stop container for a given id.
	"""
	LOG.info("STOP +job stop %s" % id)
	
	query = self.db.get_container(id)
	if query.status == "stoped":
	    return
	self.db.update_container(id,status="stoping") 
	status = self.driver.stop(query.uuid)
	if status == 204:
	    self.db.update_container(id,status="stoped")
    
	LOG.info("STOP -job stop %s" % id)

    def destroy(self,name):
	"""
	destroy a temporary container by a given name.
	"""
	self.driver.stop(name)
	self.driver.delete(name)
