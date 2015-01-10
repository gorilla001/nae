

__all__ = ['BodyEmptyError',
           'ParamNoneError',
           'ImageLimitExceedError',
           'ContainerLimitExceed',
           'ParseError',
           'NoValidHost',
           'NoValidIPAddress',
           'NetWorkError',
]

class BaseException(Exception):
    msg = "A unknown exception occurred."
    def __init__(self,message=None):
        if not message:
            message = self.msg

        super(BaseException,self).__init__(message)


class BodyEmptyError(BaseException):
    msg = "Body can not be None."

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


class NoValidHost(BaseException):
    msg = "No container node available." 

class NoValidIPAddress(Exception):
    msg = "No IPAddress left."

class NetWorkError(Exception):
    def __init__(self,msg):
	self.msg = msg

    def __str__(self):
	return self.msg
