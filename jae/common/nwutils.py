import commands
from jae.common import cfg
from jae.common.exception import NetWorkError

CONF = cfg.CONF

def create_virtual_iface(uuid,addr):
    """create virtual interface with address addr"""
    prefix = CONF.interface_name
    if not prefix:
	raise NetWorkError("no interface specified!")
    vif = "%s:%s" % (prefix,uuid)
    status,output = commands.getstatusoutput('ifconfig %s %s' % (vif,addr))
    if status != 0:
	raise NetWorkError("create virtual interface error %s " % output)

def delete_virtual_iface(uuid):
    pass
