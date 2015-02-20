#!/usr/bin/env python
# This file is used for rpc

import kombu
import kombu.entity
import kombu.messaging

class Connection(object):
    def __init__(self):
        self.connection = kombu.connection.BrokerConnection(hostname='localhost',
                                                            port=5672,
                                                            userid='guest',
                                                            password='guest',
                                                            virtual_host='/')
        self.channel = self.connection.channel()

def Publisher(object):
    """Base Publisher Class"""
    def __init__(self,channel,exchange_name,routing_key,**kwargs):
        """Init the Publisher class with the exchange_name,routing_key,
           and kwargs options
        """
        self.channel = channel
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.kwargs = kwargs
        self.exchange = kombu.entity.Exchange(name=self.exchange_name,
                                              **self.kwargs)
        self.producer = kombu.messaging.Producer(exchange=self.exchange,
                                                 channel=self.channel,
                                                 routing_key=self.routing_key)

    def send(self,msg):
        self.producer.publish(msg)

def TopicPublisher(Publisher):
    """Topic Publisher Class"""
    def __init__(self,channel,topic,**kwargs):
        """Init a 'topic' publisher"""
        options = {'durable': True,
                   'auto_delete': False,
                   'exclusive': False}
        super(TopicPublisher,self).__init__(channel)

class TopicConsumer(object):
    def __init__(self,channel,topic,callback):
        self.channel = channel
        self.callback = callback
        self.exchange = kombu.entity.Exchange(name='container',
                                              type='topic',
                                              durable=True,
                                              auto_delete=False)
        self.queue = kombu.entity.Queue(name=topic,
                                        exchange=self.exchange,
                                        routing_key=topic,
                                        channel=self.channel,
                                        durable=False,
                                        auto_delete=False,
                                        exclusive=False)
        self.queue.declare()

    def consume(self):
        self.queue.consume(callback=None)



def call(msg):
    return NotImplementedError()


def cast(msg):
    pass
