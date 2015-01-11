import webob.exc
import os 

from jae.common import cfg
from jae.common import log as logging
from jae.common.cfg import Int, Str
from jae.common import utils
from jae.common.mercu import MercurialControl 

from jae.image import driver
from jae import base 


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Manager(base.Base):
    def __init__(self):
	super(Manager,self).__init__()

	self.driver = driver.API()
	self.mercurial = MercurialControl()


    def service_init(self):
        """Create rpc producer and customers here."""
        return NotImplementedError()
    
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
		desc,
		repos,
		branch,
		user_id):
	"""create new image."""

	LOG.info("BUILD +job build %s" % name)
        repo_name=os.path.basename(repos)
	#user_home = os.path.join("/home",user_id)
        user_home = os.path.join(os.path.expandvars('$HOME'),user_id)
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

    def delete(self,id):
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
    def edit(self,kwargs,host,name,port):
        """edit image online."""
        resp = self.driver.create(name,kwargs) 
        if resp.status_code == 201:
             container_uuid = resp.json()['Id']
             resp = self.driver.start(host,port,container_uuid)
             if resp.status_code != 204:
                 LOG.debug("start for-image-edit container failed")
        else:
	     LOG.debug("create for-image-edit container failed") 


    def destroy(self,name):
	"""
	destroy a temporary container by a given name.
	"""
        self.driver.destroy(name)

    def commit(self,image_id,repository,tag,container_name):
        """commit image for online edit.""" 
        LOG.info("COMMIT +job commit %s" % container_name)
        resp = self.driver.commit(container_name,repository,tag)
        if resp.status_code == 201:
            """update image uuid."""
            image_uuid = resp.json()['Id'] 
            self.db.update_image(id=image_id,
                                  uuid=image_uuid)
            """commit ok,tag the image to repository."""
            LOG.info("TAG +job tag image %s to repository" % image_id)
            status,new_repository = self.driver.tag(repository,tag)
            if status == 201:
                LOG.info("TAG -job tag image %s = OK" % image_id)
                LOG.info("PUSH +job push %s" % tag)
                push_status = self.driver.push(new_repository,tag)
                if push_status == 200:
                    LOG.info("PUSH -job push %s = OK" % tag)
                    self.db.update_image(id=image_id,status="ok")
                    LOG.info("COMMIT -job commit %s = OK" % container_name)
                else:
                    LOG.info("PUSH -job push %s = ERR" % tag)
                    self.db.update_image(id=image_id,status="error")
            self.driver.destroy(container_name)
                     
        if resp.status_code == 404:
            image_uuid = resp.json()['Id'] 
            self.db.update_image(id=image_id,
                                  uuid=image_uuid,
                                  status="error")
            LOG.info("COMMIT -job commit %s = ERR" % container_name)
        
