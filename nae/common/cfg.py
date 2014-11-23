    
from nae.common.parser import BaseParser

class ConfigParser(BaseParser):
    def __init__(self):
	super(ConfigParser, self).__init__()
        self._opts = {}

    def __call__(self,conf):
	self._parse_config_file(conf)

    def __getattr__(self,key):
	return self._opts[key]

    def _parse_config_file(self,conf):
	
	with open(conf) as conf:
	    self.parse(conf) 

    def assignment(self,key,value):
	self._opts[key] = value


CONF=ConfigParser()

def setup_config():
    return CONF('/etc/nae/nae.conf')
