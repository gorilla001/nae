import mercurial.commands
import mercurial.ui
import mercurial.hg
import os
from jae.common import log as logging
from jae.common import cfg

CONF=cfg.CONF

LOG=logging.getLogger(__name__)

class MercurialControl(object):
    def __init__(self):
        self._ui = mercurial.ui.ui()
        self.path=CONF.static_file_path
    def clone(self,user_name,repo_path):
        source = repo_path
        path = os.path.join(self.path,user_name)
        dest = os.path.join(path,os.path.basename(repo_path)) 
        try:
            LOG.debug('clone docker file from %s' % repo_path)
            mercurial.commands.clone(self._ui,
                           str(source),
                           str(dest),
                           pull=False,
                           uncompressed=False,
                           rev=False,
                           noupdate=False)
        except Exception,error:
            LOG.error('could not clone repo:%s' % repo_path)
            LOG.error(error)
	    raise 
    def pull(self,user_name,repo_path):
        source = repo_path
        path = os.path.join(self.path,user_name)
        local_repo_path = os.path.join(path,
                                       os.path.basename(repo_path)) 
        repo=mercurial.hg.repository(self._ui,
                                     local_repo_path)
	try:
            mercurial.commands.pull(self._ui,
                                    repo,
                                    source=source)
        except Exception,error:
            LOG.error('could not pull repo:%s' % repo_path)
            LOG.error(error)
	    raise
    def update(self,user_name,repo_path,branch=None):
        path = os.path.join(self.path,user_name)
        local_repo_path = os.path.join(path,os.path.basename(repo_path)) 
        repo=mercurial.hg.repository(self._ui,
                                     local_repo_path)
	try:
            mercurial.commands.update(self._ui,
                                      repo,
                                      rev=branch,clean=True)
        except RepoError as err:
	    LOG.error(err)
	    raise

