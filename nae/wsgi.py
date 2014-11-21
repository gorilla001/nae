import webob.dec
import routes.middleware
from eventlet import wsgi
import eventlet
import os
from nae import log
import logging
from paste.deploy import loadapp


LOG=logging.getLogger('eventlet.wsgi.server')

class Router(object):
    """ WSGI middleware that maps incoming requests to WSGI apps. """
    
    def __init__(self,mapper):
        self.mapper=mapper
        self._router=routes.middleware.RoutesMiddleware(self._dispatch,self.mapper)

    @classmethod
    def factory(cls,global_config,**local_config):
        return cls()
    
    @webob.dec.wsgify
    def __call__(self,req):
        return self._router

    @staticmethod
    @webob.dec.wsgify
    def _dispatch(req):
        match = req.environ['wsgiorg.routing_args'][1]
	if not match:
	    return webob.exc.HTTPNotFound()
	app=match['controller']
	return app

class Controller(object):
    @staticmethod
    def get_method(request):
	return request.environ['wsgiorg.routing_args'][1]['action']

    @webob.dec.wsgify
    def __call__(self,request):
        _method=self.get_method(request)
        method=getattr(self,_method)     

        response=webob.Response()
        result_json=method(request)
        response.json=result_json
        return response

class Resource(object):
	def __init__(self,controller):
	    self.controller = controller

	@webob.dec.wsgify
	def __call__(self,request):
	    action_args = self.get_action_args(request.environ)
	    action = action_args.pop('action',None)
	    try:
	        method=getattr(self.controller,action)
	    except AttributeError:
		raise

	    return dispatch(request,method,action_args) 

	def get_action_args(self,env):
	    try:
	        args = env['wsgiorg.routing_args'][1].copy()
	    except KeyError:
		raise
	    try:
	        del args['controller']
	    except KeyError:
	        pass
	    try:
	        del args['format']
	    except KeyError:
	        pass

	    return args	
	
	@staticmethod
	def dispatch(request,method,action_args):
	    return method(request,**action_args)
	    


class Server(object):

	default_pool_size = 1000

	def __init__(self,app,host,port,backlog=128):
            self._server = None
            self.app = app
            self._protocol = eventlet.wsgi.HttpProtocol
            self.pool_size = self.default_pool_size
            self._pool=eventlet.GreenPool(self.pool_size)
            self._logger = log.getlogger()
            self._wsgi_logger=log.WSGILogger(self._logger)
	        
            bind_addr = (host,port)
            self._socket=eventlet.listen(bind_addr,family=2,backlog=backlog)

	def start(self):
	    dup_socket = self._socket.dup()
	    wsgi_kwargs = {
            		'func': eventlet.wsgi.server,
            		'sock': dup_socket,
            		'site': self.app,
            		'protocol': self._protocol,
            		'custom_pool': self._pool,
            		'log': self._wsgi_logger,
            		'debug': False
            		}
	    self._server = eventlet.spawn(**wsgi_kwargs)

	def stop(self):
	    self._pool.resize(0)
	    self._server.kill()

	def wait(self):
	    self._pool.waitall()
	    self._server.wait()

class Loader(object):
	def __init__(self,config_path=None):
	    self.config_file = '/etc/nae/api-paste.ini'
	    self.config_path=os.path.abspath(self.config_file)
	def load_app(self,name):
	    return loadapp("config:%s" % self.config_path,name=name)
