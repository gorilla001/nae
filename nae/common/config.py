import ConfigParser
import sys 
import os

try:
    parser=ConfigParser.SafeConfigParser()
    if parser.read(os.path.abspath("/etc/nae/nae.conf")) == [] :
        raise IOError("Cannot open config file")
    try:

        docker_host=parser.get("default","docker_host")
        docker_port=parser.get("default","docker_port")
		
        
        port=parser.get("default","port")
        workers=parser.get("default","workers")

        PortRange = parser.get("default","port_range")

        DNS=parser.get("default","dns")

        HOST=parser.get("default","host")

	PHP_ROOT_PATH=parser.get("default","php_root_path")
	JAVA_ROOT_PATH=parser.get("default","jave_root_path")

    except ConfigParser.NoSectionError as error:
        pass
except IOError as error:
    sys.exit(error)


