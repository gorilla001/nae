from nae.common import cfg
from nae.common import log as logging

cfg.parse_config()
logging.setup()

from nae.common import rpc

topic = 'compute.test'

msg = {'method': 'check', 'args': {'hello': 'world'}}

rpc.cast(topic, msg)
