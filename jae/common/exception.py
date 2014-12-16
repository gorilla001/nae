
class BodyEmptyError(Exception):
    def __init__(self,message):
        self.msg = message
    def __str__(self):
        return self.msg

class ParamNoneError(Exception):
    def __init__(self,param):
	self.param = param
    def __str__(self):
        return '%s cannot be None!' % self.param

class ImageLimitExceedError(Exception):
    def __init__(self,message):
        self.msg = message
    def __str__(self):
        return self.msg

class ContainerLimitExceeded(Exception):
    def __init__(self):
	self.msg = 'container limit exceeded!!!'
  
    def __str__(self):
	return self.msg

class ParseError(Exception):
    def __init__(self, message, lineno, line):
        self.msg = message
        self.line = line
        self.lineno = lineno

    def __str__(self):
        return 'at line %d, %s: %r' % (self.lineno, self.msg, self.line)


class NoValidHost(Exception):
    def __init__(self,message):
	self.msg = message

    def __str__(self):
	return self.msg

class NoValidIPAddress(Exception):
    def __init__(self,message):
	self.msg = message

    def __str__(self):
	return self.msg
