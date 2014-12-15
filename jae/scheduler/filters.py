from telnetlib import Telnet
import socket

from jae.common import log as logging

LOG = logging.getLogger(__name__)

class StatusFilter(object):
    def host_passes(self,host):
	if not self.service_is_up(host):
	    LOG.debug("host %s is down,ignore..." % host.host)
	    return False
        return True
	
    def service_is_up(self,host):
	telnet = Telnet() 
	try:
	    telnet.open(host.host,host.port)
	except socket.error: 
	    return False
	finally:
	    telnet.close()
	
	return True
