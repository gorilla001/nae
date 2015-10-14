import sys

from eventlet import event
from eventlet import greenthread
from nae.common import log as logging

LOG = logging.getLogger(__name__)


class LoopingCall(object):
    def __init__(self, func=None, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.func = func
        self._running = False
        self.done = event.Event()

    def start(self, interval):
        self._running = True

        def _inner():
            try:
                while self._running:
                    self.func(*self.args, **self.kwargs)
                    """It is important to check `self._running`'s value, if it is False, break."""
                    if not self._running:
                        break

                    greenthread.sleep(interval)
            except Exception:
                LOG.error("Periodic task %s running failed..." %
                          self.func.__name__)
                self.done.send_exception(*sys.exec_info())

        greenthread.spawn(_inner)

    def stop(self):
        self._running = False

    def wait(self):
        self.done.wait()

    @property
    def func_name(self):
        return self.func.__name__
