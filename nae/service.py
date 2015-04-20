import os
from nae import wsgi
import eventlet
import time
import signal
from nae.common import log as logging
from nae.common import cfg
from nae.common.cfg import Int
from nae.common import rpc
from nae.common import importutils
from nae.common import loopingcall

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

class WSGIService(object):
    def __init__(self,name):
	self.name = name
        self.loader = wsgi.Loader()
        self.app = self.loader.load_app(self.name)
        self.host = getattr(CONF,"%s_bind_host" % self.name)
        self.port = Int(getattr(CONF,"%s_bind_port" % self.name)) 
        self.workers = Int(CONF.workers) 
        self.server = wsgi.Server(self.name,
                                  self.app,
        	                  self.host,
        	                  self.port)
    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

    def wait(self):
        self.server.wait()
				
class ServerWrapper(object):
	def __init__(self,server,workers):
		self.server = server
		self.workers = workers
		self.children = set()	 

class Launcher(object):
	@staticmethod
	def run_service(service):
		service.start()
		service.wait()

class ProcessLauncher(object):
    def __init__(self,wait_interval=0.01):
        self.children = {}
        rfd,self.writepipe = os.pipe()
        self.running = True
	self.wait_interval=wait_interval

        signal.signal(signal.SIGTERM,self._handle_signal)
        signal.signal(signal.SIGINT,self._handle_signal)
        """	
	SIGKILL can not be catch 
        """	
        #signal.signal(signal.SIGKILL,self._handle_signal)

    def _handle_signal(self,signo,frame):
	LOG.debug("master recived SIGTERM or SIGNIT...")
        self.running = False

    def _child_process(self,server):
        eventlet.hubs.use_hub()
		
        os.close(self.writepipe)

	signal.signal(signal.SIGTERM,signal.SIG_DFL)
	signal.signal(signal.SIGINT,signal.SIG_IGN)

        launcher = Launcher()
        launcher.run_service(server)

    def _start_child(self,wrap):
        pid = os.fork()
        if pid == 0:
            try:
                self._child_process(wrap.server)
            finally:
                wrap.server.stop()
            os._exit(0)
        wrap.children.add(pid)
        self.children[pid]=wrap

    def _wait_child(self):
        pid,status = os.waitpid(0,os.WNOHANG)
        if pid not in self.children:
            return None
        wrap = self.children.pop(pid)
        wrap.children.remove(pid)
        return wrap
		
    def launch_server(self,server,workers=1):
        wrap = ServerWrapper(server,workers)
        while len(wrap.children) < wrap.workers:
            self._start_child(wrap)

    def wait(self):
        while self.running: 
            wrap = self._wait_child()
            if not wrap:
		eventlet.greenthread.sleep(self.wait_interval)
                continue
            while len(wrap.children) < wrap.workers:
                self._start_child(wrap)

	LOG.debug("master is going to die,kill workers first...")
        for pid in self.children:
            os.kill(pid,signal.SIGTERM)

        while self.children:
            self._wait_child()



class Service(object):
    
    def __init__(self, host, topic, manager, periodic_interval):
        self.host = host
        self.topic = topic
        manager_class = importutils.import_class(manager)
        self.manager = manager_class() 
        self.periodic_interval = periodic_interval
        self.timers = []
        self.conn = None


    @classmethod
    def create(cls,
               host=None,
               topic=None,
               manager=None,
               periodic_interval=None):
        """
        Create container service object use the specified options.

        :params host: the name of the node. defaults to CONF.host
        :params topic: message topic.
        :params manager: service control manager.
        :periodic_interval: periodic tasks run interval, defaults to 60 seconds.

        :returns: container service object. 
        """
        
        if not host:
            host = CONF.hostname
        if not topic:
            topic = 'compute'
        if not manager:
            manager = CONF.container_manager
        if not periodic_interval:
            periodic_interval = CONF.periodic_interval or 60

        service_obj = cls(host=host,
                          topic=topic,
                          manager=manager,
                          periodic_interval=periodic_interval)

        return service_obj

    def start(self):
        """
        This method contains the following two sections:
            1. create consumer
            2. start periodic tasks if exists   
        """

        LOG.info("Create consumer connection for service %s" % self.topic)
        self.conn = rpc.create_connection(new=True) 

        """Get callback object"""
        rpc_dispatcher = self.manager.create_rpc_dispatcher() 

        """Create direct topic consumer"""
        topic = "%s.%s" % (self.topic, self.host)
        self.conn.create_consumer(topic, rpc_dispatcher, fanout=False)

        """Start consumer to consume"""
        self.conn.consume_in_thread()

        """Start peridic tasks"""
        periodic = loopingcall.LoopingCall(self.periodic_tasks)
        periodic.start(interval=self.periodic_interval)
        self.timers.append(periodic)

    def stop(self):
        """Stop periodic tasks"""
         
        for task in self.timers:
            try:
                task.stop()
            except Exception:
                pass    
        self.timers = []

    def wait(self):
        """Wait for the task to finish"""
        
        for task in self.timers:
            try:
                task.wait()
            except Exception:
                pass

    def periodic_tasks(self):
        """Tasks to be run at a periodic interval"""
        self.manager.periodic_tasks()
        
