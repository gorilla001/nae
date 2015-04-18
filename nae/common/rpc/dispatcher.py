




class RpcDispatcher(object):
    def __init__(self, callback):
        self.callback = callback
        super(RpcDispatcher, self).__init__()

    def dispatch(self, method, **kwargs):
        return getattr(self.callback, method)(**kwargs)
