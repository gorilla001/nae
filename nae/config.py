import ConfigParser
import sys 
import os

try:
    parser=ConfigParser.SafeConfigParser()
    if parser.read(os.path.abspath("config.ini")) != [] :
        pass
    else:
        raise IOError("Cannot open config file")

    try:

        docker_host=parser.get("default","docker_host")
        docker_port=parser.get("default","docker_port")
		
        
        port=parser.get("default","port")
        workers=parser.get("default","workers")

        PortRange = parser.get("default","PortRange")

        DNS=parser.get("default","DNS")

        HOST=parser.get("default","HOST")

	PHP_ROOT_PATH=parser.get("default","PHP_ROOT_PATH")
	JAVA_ROOT_PATH=parser.get("default","JAVA_ROOT_PATH")

    except ConfigParser.NoSectionError,error:
        pass
    except ConfigParser.NoSectionError as error:
        pass
except IOError as error:
    sys.exit(error)


