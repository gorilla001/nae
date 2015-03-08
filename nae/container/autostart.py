from nae import base
from nae.common import cfg
import requests


CONF=cfg.CONF

class StartManager(base.Base):
    """start containers when process starting."""
    def __init__(self):
        super(StartManager,self).__init__()

    def start_all(self):
	"""start all containers."""
	container_instances = self.db.get_containers()
	if container_instances:
	    for instance in container_instances:
		if instance.uuid:
		    self.start(instance.uuid)

    def start(self,uuid):
	"""start container."""
	host,port = CONF.host,CONF.port
	requests.post("http://%s:%s/containers/%s/start" \
		     % (host,port,uuid))
