import uuid
import copy
from sqlalchemy.exc import IntegrityError

from jae import wsgi
from jae import base
from jae.common.timeutils import isotime
from jae.common.response import Response, ResponseObject
from jae.common import log as logging

LOG = logging.getLogger(__name__)

class Controller(base.Base):

    def __init__(self):
	super(Controller,self).__init__()

    def index(self,request):
        """show all repos by project id."""
        repos=[]
        project_id = request.GET.get('project_id')
        query = self.db.get_repos(project_id=project_id)
        for item in query: 
            repo={
                'id':item.id,
                'repo_path':item.repo_path,
                'created':isotime(item.created),
                }
            repos.append(repo)

        return ResponseObject(repos) 

    def show(self,request,id):
        """show repos info by repos id."""
        query = self.db.get_repo(id)
        if query is None:
	    return {}
        repo={'id':query.id,
              'repo_path':query.repo_path,
              'project_id':query.project_id,
              'created':isotime(query.created)}

	return ResponseObject(repo)

    def create(self,request,body):
        """create repos by body dict."""
        project_id=body.get('project_id')
        repo_path=body.get('repo_path')
        project = self.db.get_project(id=project_id)
	try:
            self.db.add_repo(dict(
		id = uuid.uuid4().hex,
                repo_path= repo_path,
                project = copy.deepcopy(project)))
        except IntegrityError,err:
	    LOG.error(err)
	    return Response(500) 

        return Response(200) 

    def delete(self,request,id):
        """delete repos by id."""
        self.db.delete_repo(id)

        return Response(200) 

def create_resource():
    return wsgi.Resource(Controller())

