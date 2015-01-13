from netaddr import IPRange, IPAddress

from jae.common import cfg
from jae import db
from jae.base import Base
from jae.common import exception

CONF=cfg.CONF

FIXED_RANGE=None

class NetworkManager(Base):
    def get_fixed_ip(self):
	global FIXED_RANGE
	if not FIXED_RANGE:
	    FIXED_RANGE = self.get_fixed_range() 
	
	query = self.db.get_containers()
        if query:
            for item in query:
                if item.fixed_ip:
                    if IPAddress(item.fixed_ip) in FIXED_RANGE:
                        FIXED_RANGE.remove(IPAddress(item.fixed_ip))
	try:
	    return str(FIXED_RANGE[0])	
	except IndexError:
	    raise exception.NoValidIPAddress(msg='Ip resource has used up :(.')

    def get_fixed_range(self):
	ip_resource_pool = CONF.ip_resource_pool 	
	if not ip_resource_pool:
	    raise exception.NoValidIPAddress(msg='Ip resource pool is None,
                                                  You must specified a ip resource range.')
	
	start,_,end=ip_resource_pool.rpartition("-")

	ip_range = IPRange(start,end)

	return list(ip_range)
