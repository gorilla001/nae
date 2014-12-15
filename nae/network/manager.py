import netaddr
from netaddr import IPRange, IPAddress

from nae.common import cfg
from nae import db
from nae.base import Base
from nae.common import exception

CONF=cfg.CONF

FIXED_RANGE=None

class NetworkManager(Base):
    def get_fixed_ip(self):
	global FIXED_RANGE
	if not FIXED_RANGE:
	    FIXED_RANGE = self.get_fixed_range() 
	
	query = self.db.get_containers()
	if not query:
	    for item in query:
		if IPAddress(item.fixed_ip) in FIXED_RANGE:
		    FIXED_RANGE.remove(IPAddress(item.fixed_ip))

	try:
	    return str(FIXED_RANGE[0])	
	except IndexError:
	    raise NoValidIPAddress(msg='ip resource used up')

    def get_fixed_range(self):
	ip_resource_pool = CONF.ip_resource_pool 	
	if not ip_resource_pool:
	    raise NoValidIPAddress(msg='ip resource pool is None')
	
	start,_,end=ip_resource_pool.rpartition("-")

	ip_range = IPRange(start,end)

	return list(ip_range)
