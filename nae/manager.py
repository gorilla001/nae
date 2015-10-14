import eventlet
import time

from nae.common import log as logging
from nae.common.rpc import dispatcher as rpc_dispatcher

LOG = logging.getLogger(__name__)

DEFAULT_INTERVAL = 60.0


def periodic_task(*args, **kwargs):
    """
    Decorator to indicate that a method is a periodic task.

    This decorator can be used in two ways:

        1. Without arguments '@periodic_task', this whill be run on default
           interval of 60 seconds.

        2. With arguments: @periodic_task(periodic_interval = N)
           this will be run on every N seconds.
    """

    def decorator(f):
        f._periodic_task = True
        f._periodic_interval = kwargs.pop('periodic_interval',
                                          DEFAULT_INTERVAL)
        f._periodic_last_run = time.time()

        return f

    if kwargs:
        return decorator
    return decorator(args[0])


class ManagerMeta(type):
    def __init__(cls, name, bases, dict):
        """Metaclass that allows us to collect decorated periodic tasks."""
        super(ManagerMeta, cls).__init__(name, bases, dict)

        try:
            cls._periodic_tasks = cls._periodic_tasks[:]
        except AttributeError:
            cls._periodic_tasks = []

        try:
            cls._periodic_interval = cls._periodic_interval.copy()
        except AttributeError:
            cls._periodic_interval = {}

        try:
            cls._last_run = cls._last_run.copy()
        except AttributeError:
            cls._last_run = {}

        for value in cls.__dict__.values():
            if getattr(value, '_periodic_task', False):
                task = value
                name = task.__name__
                if task._periodic_interval < 0:
                    LOG.info("""Skipping periodic task %(task)s because
                                 its interval is negative""",
                             {'task': task.__name__})
                    continue
                """A periodic interval of zero indicates that this task should be 
                   run on default interval to avoid running too frequently"""
                if task._periodic_interval == 0:
                    task._periodic_interval = DEFAULT_INTERVAL

                cls._periodic_tasks.append((name, task))
                cls._periodic_interval[name] = task._periodic_interval
                cls._last_run[name] = task._periodic_last_run


class Manager(object):
    __metaclass__ = ManagerMeta

    def __init__(self):
        super(Manager, self).__init__()
        self.version = '1.0.0'

    def periodic_tasks(self):
        """Tasks to be run at a periodic interval"""
        for task_name, task in self._periodic_tasks:
            full_task_name = '.'.join([self.__class__.__name__, task_name])

            interval = self._periodic_interval[task_name]
            last_run = self._last_run[task_name]

            spancing = time.time() - last_run
            if spancing < interval:
                continue
            LOG.debug("Running periodic task %(full_task_name)s", locals())

            try:
                task(self)
                """After finish a task, allow manager to do other work.This method will invoke the hub's switch to
                   let anyother greenthreads to schedule."""
                eventlet.sleep(0)
            except Exception as ex:
                LOG.error("Error during %(full_task_name)s", locals())
                return

            self._last_run[task_name] = time.time()

    def create_rpc_dispatcher(self):
        """Get the rpc dispatcher"""
        return rpc_dispatcher.RpcDispatcher(self)
