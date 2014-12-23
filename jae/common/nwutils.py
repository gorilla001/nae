import commands
from jae.common import cfg
from jae.common.exception import NetWorkError
import os

CONF = cfg.CONF

NET_SCRIPT_PATH="/etc/sysconfig/network-scripts/"

def create_virtual_iface(uuid,addr):
    """create virtual interface with address addr"""
    prefix = CONF.interface_name
    if not prefix:
	raise NetWorkError("no interface specified!")
    vif = "%s:%s" % (prefix,uuid)
    status,output = commands.getstatusoutput('ifconfig %s %s' % (vif,addr))
    if status != 0:
	raise NetWorkError("create virtual interface error %s " % output)

    vif_file_name = "%s-%s" % ("ifcfg",vif)
    netmask=CONF.netmask or '255.255.255.0'
    with open(os.path.join(NET_SCRIPT_PATH,vif_file_name),'w') as vif_file:
        vif_file.write("DEVICE=%s\n" % vif)
        vif_file.write("BOOTPROTO=static\n")
        vif_file.write("ONBOOT=yes\n")
        vif_file.write("TYPE=Ethernet\n")
        vif_file.write("IPADDR=%s\n" % addr)
        vif_file.write("NETMASK=%s\n" % netmask)


def delete_virtual_iface(uuid):
    """delete virtual interface and network-script"""
    prefix = CONF.interface_name
    if not prefix:
       raise NetWorkError("no interface specified!")
    if len(uuid) > 8:
       uuid = uuid[:8]
    vif = "%s:%s" % (prefix,uuid)
    status,output = commands.getstatusoutput('ifconfig %s down' % vif)
    if status != 0:
       raise NetWorkError("delete virtual interface error %s " % output)
    vif_file_name = "%s-%s" % ("ifcfg",vif)
    try:
        os.remove(os.path.join(NET_SCRIPT_PATH,vif_file_name))
    except OSError,err:
        if err.errno == 2:
            pass
        else:
	    raise
