class ParseError(Exception):
    def __init__(self, message, lineno, line):
        self.msg = message
        self.line = line
        self.lineno = lineno

    def __str__(self):
        return 'at line %d, %s: %r' % (self.lineno, self.msg, self.line)

class BaseParser(object):
    lineno = 0
    
    def parse(self,conf):
	"""
        The config parse method.
	"""
        for line in conf:
	    self.lineno += 1	

            line = line.rstrip()
	    if not line:
	        continue
	    if line[0] == '[':
		self._check_section(line)

	    elif line[0] in '#;':
	        continue
	    else:
	        key,value = self._split_key_value(line)
	        if not key:
		    raise ParseError('Key cannot be empty',self.lineno,line)
	        self.assignment(key, value)

    def _check_section(self,line):
	if line[-1] != ']':
	    raise ParseError('Invalid section (must end with ])',
			     self.lineno,line)

	if len(line) == 2:
	    raise ParseError('Empty section name',self.lineno,line)

    def _split_key_value(self,line):
	key,_,value = line.rpartition('=')
	return key.strip(),value.strip()

    def assignment(self,key,value):
	raise NotImplementedError()
