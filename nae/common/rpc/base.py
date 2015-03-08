class Connection(object):
    """Base connection"""

    def create_consumer(self, topic, proxy, fanout=False):
        """Create a consumer on this connection."""

        raise NotImplementedError()

    def consume_in_thread(self):
        """Spawn a thread to handle incoming messages."""
        raise NotImplementedError()
