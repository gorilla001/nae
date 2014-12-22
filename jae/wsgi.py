import os
import json
import webob
import webob.dec
import routes.middleware
import eventlet
from eventlet import wsgi
from paste.deploy import loadapp

from jae.common import log as logging
from jae.common import cfg
from jae.common.exception import BodyEmptyError

LOG=logging.getLogger(__name__)

CONF=cfg.CONF

class Router(object):
    """ WSGI middleware that maps incoming requests to WSGI apps. """
    
    def __init__(self,mapper):
        self.mapper=mapper
        self.mapper.redirect("","/")
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
	    return webob.Response('{"error" : "404 Not Found"}')
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

	response=JsonResponse()
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
	    body=self.get_body(request)
	    action_args.update(body)

	    return self._process_stack(request,method,action_args) 

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

        def get_body(self,request):
	    if len(request.body) == 0:
		return {}
	    return {'body':json.loads(request.body)}

        def _process_stack(self,request,method,action_args):
            response = self.dispatch(request,method,action_args) 
	    
	    return response

	@staticmethod
	def dispatch(request,method,action_args):
	    return method(request,**action_args)
	    


class Server(object):

	default_pool_size = 1000

	def __init__(self,name,app,host,port,backlog=128):
	    self.name = name
            self._server = None
            self.app = app
            self._protocol = eventlet.wsgi.HttpProtocol
            self.pool_size = self.default_pool_size
            self._pool=eventlet.GreenPool(self.pool_size)
            self._wsgi_logger=logging.WSGILogger(logging.getLogger())
	        
            bind_addr = (host,port)
            self._socket=eventlet.listen(bind_addr,family=2,backlog=backlog)

	    """
            register host for scheduler.
            """
	    if self.name == 'container':
		"""register host."""
		from jae.container import register
	    	self._register = register.Register()
            	(self.host, self.port) = self._socket.getsockname()
            	self._register.register(self.host,self.port)
		"""start containers on this host."""
		from jae.container import autostart
		self._start_manager = autostart.StartManager()
		self._start_manager.start_all()

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
	def __init__(self):
	    self.config = CONF.api_paste_file 
	def load_app(self,name):
	    return loadapp("config:%s" % self.config,name=name)
