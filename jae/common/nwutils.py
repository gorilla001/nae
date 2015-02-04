#import commands
from jae.common import cfg
from jae.common import log as logging
from jae.common.exception import NetWorkError
import os
import subprocess

CONF = cfg.CONF
LOG=logging.getLogger(__name__)

#TEMP_PATH="/tmp"

#NET_SCRIPT_PATH="/etc/sysconfig/network-scripts/"

DEFAULT_NET_MASK="255.255.255.0"

#not used anymore
#def create_virtual_iface(uuid,addr):
#    """create virtual interface with address addr"""
#    prefix = CONF.interface_name
#    if not prefix:
#	raise NetWorkError("no interface specified!")
#    vif = "%s:%s" % (prefix,uuid)
#    status,output = commands.getstatusoutput('sudo ifconfig %s %s' % (vif,addr))
#    if status != 0:
#	raise NetWorkError("create virtual interface error %s " % output)
#
#    vif_file_name = "%s-%s" % ("ifcfg",vif)
#    netmask=CONF.netmask 
#    if not netmask:
#        netmak=DEFAULT_NET_MASK
#
#    with open(os.path.join(TEMP_PATH,vif_file_name),'w') as vif_file:
#        vif_file.write("DEVICE=%s\n" % vif)
#        vif_file.write("BOOTPROTO=static\n")
#        vif_file.write("ONBOOT=yes\n")
#        vif_file.write("TYPE=Ethernet\n")
#        vif_file.write("IPADDR=%s\n" % addr)
#        vif_file.write("NETMASK=%s\n" % netmask)
#    os.system("sudo mv %s %s" % (os.path.join(TEMP_PATH,vif_file_name),NET_SCRIPT_PATH))
#
#
#def delete_virtual_iface(uuid):
#    """delete virtual interface and network-script"""
#    prefix = CONF.interface_name
#    if not prefix:
#       raise NetWorkError("no interface specified!")
#    if len(uuid) > 8:
#       uuid = uuid[:8]
#    vif = "%s:%s" % (prefix,uuid)
#    status,output = commands.getstatusoutput('sudo ifconfig %s down' % vif)
#    if status != 0:
#       raise NetWorkError("delete virtual interface error %s " % output)
#    vif_file_name = "%s-%s" % ("ifcfg",vif)
#    try:
#        os.system("sudo rm -f %s" % (os.path.join(NET_SCRIPT_PATH,vif_file_name)))
#    except:
#        """raise all errors"""
#        raise

def get_default_gateway():
    """Get the default route."""
    import netifaces
    gws=netifaces.gateways()

    return gws['default'][netifaces.AF_INET][0]

def inject_fixed_ip(uuid,addr):
    """Inject fixed ip to container instance.This method is similar to `pipework`
       but more simple.
       Generally contains the following four step:
           - create veth pair, one is external and the other is internal.
             >>ip link add web-int type veth peer name web-ext
           - add external veth to bridge `br0`.
             >>brctl addif br0 web-ext
           - add internal veth to container and rename to `eth1`.
             >>ip link set netns {{PID}} dev web-int
             >>nsenter -t {{PID}} -n ip link set web-int name eth1
           - add fixed ip addr for container's internal veth `eth1`.
             >>nsenter -t {{PID}} -n ip addr add ipaddr/netmask dev eth1
       You can also use dhcp for container ip allocated,as:
           >>nsenter -t {{PID}} -n -- dhclient -d eth1
    """
       	
    if len(uuid) > 8:
	uuid = uuid[:8]
    uuid_reverse = uuid[::-1]
    veth_int = "%s%s" % ("veth",uuid_reverse)
    veth_ext = "%s%s" % ("veth",uuid) 

    """First create veth pair: web-int and vethuuid"""
    try:
        LOG.info("Create veth pair: %s and %s" % (veth_int,veth_ext))
        subprocess.check_call("sudo ip link add %s type veth peer name %s" % (veth_int,veth_ext),shell=True) 
    except subprocess.CalledProcessError:
	raise

    """Second add external veth to bridge `br0`""" 
    try:
        LOG.info("Attach external veth %s to bridge `br0`" % veth_ext)
        subprocess.check_call("sudo brctl addif br0 %s" % veth_ext,shell=True)
    except subprocess.CalledProcessError:
        raise

    """Get container's pid namespace"""
    try:
        LOG.info("Get container's namespace pid")
        pid=subprocess.check_output("sudo docker inspect --format '{{.State.Pid}}' %s" % uuid,shell=True) 
	LOG.info("Pid is %s" % pid.strip())
    except subprocess.CalledProcessError:
        raise

    """Add internal veth web-int to container"""
    try:
        LOG.info("Attach internal %s to container" % veth_int)
	subprocess.check_call("sudo ip link set netns %s dev %s" % (pid.strip(),veth_int),shell=True)
    except subprocess.CalledProcessError:
	raise

    """Rename internal veth web-int to eth1"""
    try:
        LOG.info("Rename internal veth %s to eth1" % veth_int)
	subprocess.check_call("sudo nsenter -t %s -n ip link set %s name eth1" % (pid.strip(),veth_int),shell=True)
    except subprocess.CalledProcessError:
	raise

    """Set internal veth to UP"""
    try:
        LOG.info("UP internal veth eth1")
	subprocess.check_call("sudo nsenter -t %s -n ip link set eth1 up" % pid.strip(),shell=True)
    except subprocess.CalledProcessError:
	raise
    
    """Set external veth to UP"""
    try:
        LOG.info("UP external %s" % veth_ext)
	subprocess.check_call("sudo ip link set %s up" % veth_ext,shell=True)
    except subprocess.CalledProcessError:
	raise

    """Set fixed ip to internal veth `eth1`"""
    IP_ADDR="%s/%s" % (addr,DEFAULT_NET_MASK)
    try:
        LOG.info("Attach fixed IP to internal veth eth1")
	subprocess.check_call("sudo nsenter -t %s -n ip addr add %s dev eth1" % (pid.strip(),IP_ADDR),shell=True)
    except subprocess.CalledProcessError:
	raise

    """Set default gateway to br0's gateway"""
    DEFAULT_GATEWAY=get_default_gateway()
    try:
        LOG.info("Set default gateway to %s" % DEFAULT_GATEWAY)
        subprocess.check_call("sudo nsenter -t %s -n ip route del default" % pid.strip(),shell=True)
        subprocess.check_call("sudo nsenter -t %s -n ip route add default via %s dev eth1" %(pid.strip(),DEFAULT_GATEWAY),shell=True)
    except subprocess.CalledProcessError:
        raise
