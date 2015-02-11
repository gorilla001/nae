from jae import db 
from jae.common import cfg
from jae.common import log as logging
from jae.common.exception import  NetWorkError
import uuid
import netifaces
from sqlalchemy.exc import IntegrityError

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

class Register(object):
    def __init__(self):
        self.db = db.API()

    def register(self,host,port):
	if host == '0.0.0.0':
	    host = CONF.my_id
	    if not host:
	        host = self.get_host()	
	"""
	use the last 12 bit of uuid1 to unique a machine.
	"""
	id = uuid.uuid1().hex[-12:]

        zone = CONF.current_zone
        if not zone:
            zone = 'BJ'
	try:
            self.db.register(dict(
		             id=id,
		             host=host,
		             port=port,
                             zone=zone))
	except IntegrityError:
	    """
	    already register? just update addr if needed.
	    """
	    self.db.register_update(id=id,host=host,port=port,zone=zone)
	    LOG.info('register') 

    def get_host(self):
	"""
	ifaces = netifaces.interfaces()
	nic = [ i for i in ifaces if i not in 'lo'][0]
	"""
	interface_name = CONF.interface_name
	if not interface_name:	
	    raise NetWorkError("No Interface Specified!")
        addrs = netifaces.ifaddresses(interface_name)
	
	return addrs[netifaces.AF_INET][0]['addr']
