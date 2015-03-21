
from nae.common import log as logging

LOG = logging.getLogger(__name__)

class Css(object):
    def show(self, request, name):
        print '-'*10
        LOG.info("css:%s" % name)
