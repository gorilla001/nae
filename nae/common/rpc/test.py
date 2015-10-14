import kombu
from nae.common import cfg

cfg.parse_config()

CONF = cfg.CONF

params = {}
params.setdefault('hostname', CONF.rabbit_host)
params.setdefault('port', int(CONF.rabbit_port))
params.setdefault('userid', CONF.rabbit_userid)
params.setdefault('password', CONF.rabbit_password)
params.setdefault('virtual_host', CONF.rabbit_virtual_host)

connection = kombu.BrokerConnection(**params)
connection.connect()
channel = connection.channel()

topic = "compute.test"

producer = kombu.Producer(channel,
                          exchange=CONF.control_exchange,
                          routing_key=topic)

body = {}

while True:
    print 'send msg', body

    producer.publish(body, routing_key=topic, exchange=CONF.control_exchange)

    time.sleep(1)
