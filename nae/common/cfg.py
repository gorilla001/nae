    
from nae.common.parser import BaseParser

class Bool(object):
    _boolean_states = {'1': True, '0': False, 
		       'yes': True, 'no': False,
		       'true': True,'false': False, 
		       'True': True, 'False': False, 
		       'on': True,'off': False}
    def __new__(cls,value):
        return cls._boolean_states.get(value)

class Int(int):
    def __new__(cls,value):
       return int.__new__(cls,value) 

class Str(str):
    def __new__(cls,value):
        return str.__new__(cls,value)

class ConfigParser(BaseParser):
    """The configration parse object. All configrations will be collected
       in a dictionary called `_opts`. Currently only configrations those 
       in config file will be collected and command line arguments are ignored.
       Fix to collected CLI arguments also.
    """
    def __init__(self):
	super(ConfigParser, self).__init__()

        """The dictionary where all the configrations from config file are in"""
        self._opts = {}

    def __call__(self,conf):
	self._parse_config_file(conf)

    def __getattr__(self,key):
        try:
	    return self._opts[key]
        except KeyError:
	    return None

    def _parse_config_file(self,conf):
	
	with open(conf) as conf:
	    self.parse(conf) 

    def assignment(self,key,value):
	self._opts[key] = value


CONF=ConfigParser()

DEFAULT_CONF_FILE = "/etc/nae/nae.conf"

def parse_config():
    try:
        return CONF(DEFAULT_CONF_FILE)
    except:
        raise
