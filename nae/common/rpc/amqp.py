from eventlet import pools
from nae.common.rpc import base

class Pool(pools.Pool):
    """Class that implements a Pool of Connections."""

    def __init__(self, conf, connection_cls, *args, **kwargs):
        self.connection_cls = connection_cls
        self.conf = conf
        self.rpc_conn_pool_size = 100
        kwargs.setdefault("max_size", self.rpc_conn_pool_size)
        kwargs.setdefault("order_as_stack", True)
        super(Pool, self).__init__(*args, **kwargs)

    def create(self):
        return self.connection_cls(self.conf)


def create_connection_pool(conf, connection_cls):
    return Pool(conf, connection_cls) 

class ConnectionContext(base.Connection):
    def __init__(self, conf, connection_pool, pooled=True):
        self.conf = conf
        self.connection_pool = connection_pool
        self.pooled = pooled

        if self.pooled:
            self.connection = self.connection_pool.get()
        else:
            self.connection = self.connection_pool.connection_cls(self.conf)

    def __enter__(self):
        """When with ConnectionContext() is used, return self"""
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """End of 'with' statement."""
        self.connection.close()

    def create_consumer(self, topic, proxy, fanout=False):
        self.connection.create_consumer(topic, proxy, fanout)

    def consume_in_thread(self):
        self.connection.consume_in_thread()

    def __getattr__(self, key):
        """Get method from self.connection"""
        if self.connection:
            return getattr(self.connection, key)
        else:
            LOG.exception("Connection failed")


def create_connection(conf, new, connection_pool):
    """Create a connection""" 
    return ConnectionContext(conf, connection_pool, pooled=not new)


def cast(conf, topic, msg, connection_pool):
    """Throw the msg to the queue without wait for a reply"""
    with ConnectionCotext(conf, connection_pool) as conn:
        conn.topic_send(topic, msg)
