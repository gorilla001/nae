import mercurial.commands
import mercurial.ui
import mercurial.hg
import os
from nae.common import log as logging
from nae.common import cfg
import sys

reload(sys)
sys.setdefaultencoding('utf8')

CONF=cfg.CONF

LOG=logging.getLogger(__name__)

class MercurialControl(object):
    def __init__(self):
        self._ui = mercurial.ui.ui()

    def clone(self,root_path,repo_path):
        """
        Clone repository from specified path `repo_path`

        :params root_path the path where to clone the code.
        :params repo_path the path from where to clone.

        """
        source = repo_path
        dest = os.path.join(root_path,os.path.basename(repo_path)) 
        try:
            LOG.debug('Clone docker file from %s' % repo_path)
            mercurial.commands.clone(self._ui,
                           str(source),
                           str(dest),
                           pull=False,
                           uncompressed=False,
                           rev=False,
                           noupdate=False)
        except Exception,error:
            LOG.error('Could not clone repo:%s' % repo_path)
            LOG.error(error)
	    raise 

    def pull(self,root_path,repo_path):
        """
        Pull repository from `repo_path`.

        :params root_path: the path where to pull the code.
        :params repo_path: the path from where to pull.

        """
        source = repo_path
        path = root_path 
        local_repo_path = os.path.join(path,
                                       os.path.basename(repo_path)) 
        repo=mercurial.hg.repository(self._ui,
                                     local_repo_path)
	try:
            mercurial.commands.pull(self._ui,
                                    repo,
                                    source=source)
        except:
            LOG.error('Could not pull repo:%s' % repo_path)
            LOG.error(error)
	    raise
    def update(self,root_path,repo_path,branch=None):
        """
        Update repo to branch.
        :params root_path: the path where the code in.
        :params repo_path: the path where the code at.
        :params branch: the branch of the repos. 
        """
        path = root_path 
        local_repo_path = os.path.join(path,os.path.basename(repo_path)) 
        repo=mercurial.hg.repository(self._ui,
                                     local_repo_path)
	try:
            mercurial.commands.update(self._ui,
                                      repo,
                                      rev=branch,clean=True)
        except:
            LOG.error('Could not update repo %s to branch %s' % (repo_path,branch))
	    raise

