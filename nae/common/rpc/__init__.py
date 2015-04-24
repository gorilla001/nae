import sys
from nae.common import cfg
from nae.common import log as logging
from nae.common import importutils

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

_RPCIMPL = None

def _get_impl():
    global _RPCIMPL
    if _RPCIMPL is None:
        try:
            _RPCIMPL = importutils.import_module(CONF.rpc_backend)
        except ImportError:
            impl = 'nae.common.rpc.impl_kombu'
            _RPCIMPL = importutils.import_module(impl)
    return _RPCIMPL

def create_connection(new=True):
    """Create a connection to the message bus used for rpc"""
    return _get_impl().create_connection(CONF, new=new)


def cast(topic, msg):
    """Invoke a remote method that dose not return anything"""
    return _get_impl().cast(CONF, topic, msg)
