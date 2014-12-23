from telnetlib import Telnet
import socket

from jae.common import log as logging
from jae import base

LOG = logging.getLogger(__name__)

class StatusFilter(object):
    """
    very simple filter filters host by its status.
    if service on the host is up return true
    else return false.
    """
    def host_passes(self,host):
	if not self.service_is_up(host):
	    LOG.debug("host %s is down,ignore..." % host.host)
	    return False
        return True
	
    def service_is_up(self,host):
	telnet = Telnet() 
	try:
	    telnet.open(str(host.host),int(host.port))
	except socket.error: 
	    return False
	except error:
	    raise
	     
	finally:
	    telnet.close()
	
	return True

class ZoneFilter(base.Base):
    """
    very simple filter filters host by its zone.
    if host is in zone zone return true
    else return false.
    """
    def host_passes(self,host,zone):
        if host.zone != zone:
            return False 
        return True
        
