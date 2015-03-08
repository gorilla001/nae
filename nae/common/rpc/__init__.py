from nae.common import cfg
from nae.common import log as logging
from nae.common.rpc import impl_kombu

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


def create_connection(new=True):
    """Create a connection to the message bus used for rpc"""
    return impl_kombu.create_connection(CONF, new=new)
