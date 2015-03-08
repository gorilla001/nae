from nae.common import log as logging

LOG=logging.getLogger(__name__)



DEFAULT_INTERVAL = 60.0

def periodic_task(*args, **kwargs):
    def decorator(f):
        f._periodic_task = True
        f._periodic_interval = kwargsss.pop('interval',DEFAULT_INTERVAL)
        f._periodic_last_run = time.time()

        return f
    return decorator

class PeriodicTaskMeta(type):
    def __init__(cls, name, bases, dict):
        """Metaclass that allows us to collect decorated periodic tasks."""
        super(PeriodicTaskMeta,cls).__init__(name,bases,dict)

        try:
            cls._periodic_tasks = cls._periodic_tasks[:]
        except AttributeError:
            cls._periodic_tasks = []
    
        for value in cls.__dict__.values():
            if getattr(value, '_periodic_task', False):
                task = value

                if task._periodic_interval < 0:
                    LOG.info("""Skipping periodic task %(task)s because
                                 its interval is negative"""),
                             {'task': task.__name__})
                    continue
 
                """A periodic interval of zero indicates that this task should be 
                   run on default interval to avoid running too frequently"""
                if task._periodic_interval == 0:
		    task._periodic_interval = DEFAULT_INTERVAL 

                cls._periodic_tasks.append(task)

class PeriodicTask(object):
    __metaclass__ = PeriodicTaskMeta

    def __init__(self):
        super(PeriodicTasks, self).__init__() 
        
