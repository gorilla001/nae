






class LoopingCall(object):
    def __init__(self, func=None, *args, *kwargs):
        self.args = args
        self.kwargs = kwargs
        self.func = func 
        self._running = False

    def start(self, interval):
        self._running = True
        
        def _inner():
            while self._running:
                self.func(*self.args, **self.kwargs)
                greenthread.sleep(interval)

        greenthread.spawn(_inner)

    def stop(self):
        self._running = False
