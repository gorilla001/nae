
from nae.common import rpc


class Service(object):
    
    def __init__(self, host, topic, manager, periodic_interval):
        self.host = host
        self.topic = topic
        self.manager = manager
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

    def periodic_task(self):
        """Tasks to be run at a periodic interval"""
        self.manager.periodic_tasks()
        
