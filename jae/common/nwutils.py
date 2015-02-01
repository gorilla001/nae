import commands
from jae.common import cfg
from jae.common.exception import NetWorkError
import os

CONF = cfg.CONF

TEMP_PATH="/tmp"

NET_SCRIPT_PATH="/etc/sysconfig/network-scripts/"

DEFAULT_NET_MASK="255.255.255.0"

def create_virtual_iface(uuid,addr):
    """create virtual interface with address addr"""
    prefix = CONF.interface_name
    if not prefix:
	raise NetWorkError("no interface specified!")
    vif = "%s:%s" % (prefix,uuid)
    status,output = commands.getstatusoutput('sudo ifconfig %s %s' % (vif,addr))
    if status != 0:
	raise NetWorkError("create virtual interface error %s " % output)

    vif_file_name = "%s-%s" % ("ifcfg",vif)
    netmask=CONF.netmask 
    if not netmask:
        netmak=DEFAULT_NET_MASK

    with open(os.path.join(TEMP_PATH,vif_file_name),'w') as vif_file:
        vif_file.write("DEVICE=%s\n" % vif)
        vif_file.write("BOOTPROTO=static\n")
        vif_file.write("ONBOOT=yes\n")
        vif_file.write("TYPE=Ethernet\n")
        vif_file.write("IPADDR=%s\n" % addr)
        vif_file.write("NETMASK=%s\n" % netmask)
    os.system("sudo mv %s %s" % (os.path.join(TEMP_PATH,vif_file_name),NET_SCRIPT_PATH))


def delete_virtual_iface(uuid):
    """delete virtual interface and network-script"""
    prefix = CONF.interface_name
    if not prefix:
       raise NetWorkError("no interface specified!")
    if len(uuid) > 8:
       uuid = uuid[:8]
    vif = "%s:%s" % (prefix,uuid)
    status,output = commands.getstatusoutput('sudo ifconfig %s down' % vif)
    if status != 0:
       raise NetWorkError("delete virtual interface error %s " % output)
    vif_file_name = "%s-%s" % ("ifcfg",vif)
    try:
        os.system("sudo rm -f %s" % (os.path.join(NET_SCRIPT_PATH,vif_file_name)))
    except:
        """raise all errors"""
        raise
