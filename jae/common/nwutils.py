import commands
from jae.common import cfg
from jae.common.exception import NetWorkError
import os
import subprocess

CONF = cfg.CONF

TEMP_PATH="/tmp"

NET_SCRIPT_PATH="/etc/sysconfig/network-scripts/"

DEFAULT_NET_MASK="255.255.255.0"

"""not used anymore
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
"""

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
    veth="%s%s" % ("veth",uuid) 

    """First create veth pair: web-int and vethuuid"""
    try:
        subprocess.check_call("sudo ip link add web-int type veth peer name %s" % veth,shell=True) 
    except subprocess.CalledProcessError:
	raise

    """Second add external veth to bridge `br0`""" 
    try:
        subprocess.check_call("sudo brctl addif br0 %s" % veth,shell=True)
    except subprocess.CalledProcessError:
        raise

    """Get container's pid namespace"""
    try:
        pid=subprocess.check_output("sudo docker inspect --format '{{.State.Pid}}' %s" % uuid,shell=True) 
    except subprocess.CalledProcessError:
        raise

    """Add internal veth web-int to container"""
    try:
	subprocess.check_call("sudo ip link set netns %s dev web-int" % pid,shell=True)
    except subprocess.CalledProcessError:
	raise

    """Rename internal veth web-int to eth1"""
    try:
	subprocess.check_call("sudo nsenter -t %s -n ip link set web-int name eth1" % pid,shell=True)
    except subprocess.CalledProcessError:
	raise

    """Set internal veth to UP"""
    try:
	subprocess.check_call("sudo nsenter -t %s -n ip link set eth1 up" % pid,shell=True)
    except subprocess.CalledProcessError:
	raise
    
    """Set external veth to UP"""
    try:
	subprocess.check_call("sudo ip link set %s up" % veth,shell=True)
    except subprocess.CalledProcessError:
	raise

    """Set fixed ip to internal veth `eth1`"""
    IP_ADDR="%s/%s" % (addr,DEFAULT_NET_MASK)
    try:
	subprocess.check_call("sudo nsenter -t %s -n ip addr add %s dev eth1" % (pid,IP_ADDR),shell=True)
    except subprocess.CalledProcessError:
	raise
