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
    commands.getstatusoutput("echo DEVICE=%s  >> %s" % (vif,os.path.join(NET_SCRIPT_PATH,vif_file_name))) 
    commands.getstatusoutput("echo BOOTPROTO=static   >> %s" % (os.path.join(NET_SCRIPT_PATH,vif_file_name))) 
    commands.getstatusoutput("echo ONBOOT=yes      >> %s" % (os.path.join(NET_SCRIPT_PATH,vif_file_name))) 
    commands.getstatusoutput("echo TYPE=Ethernet >> %s" % (os.path.join(NET_SCRIPT_PATH,vif_file_name))) 
    commands.getstatusoutput("echo IPADDR=%s       >> %s" % (addr,os.path.join(NET_SCRIPT_PATH,vif_file_name))) 
    commands.getstatusoutput("echo NETMASK=%s       >> %s" % (netmask,os.path.join(NET_SCRIPT_PATH,vif_file_name))) 

def delete_virtual_iface(uuid):
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
    commands.getstatusoutput("rm -f %s" % os.path.join(NET_SCRIPT_PATH,vif_file_name))
