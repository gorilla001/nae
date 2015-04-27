


class Service(object):
    
    def __init__(self,periodic_interval):
        self.periodic_interval = periodic_interval
        self.timers = []
        
    def start(self):
        """Start periodic tasks"""

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
        
