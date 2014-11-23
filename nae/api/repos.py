from nae import wsgi
from nae import db
import uuid
from nae.utils import isotime
from sqlalchemy.exc import IntegrityError
import logging

LOG = logging.getLogger('eventlet.wsgi.server')

class Controller(object):

    def __init__(self):
        self.db_api=db.API()

    def index(self,request):
        repos=[]
        project_id = request.GET.get('project_id')
        query = self.db_api.get_repos(project_id=project_id)
        for item in query: 
            repo={
                'id':item.id,
                'repo_path':item.repo_path,
		'project_id':item.project_id,
                'created':isotime(item.created),
                }
            repos.append(repo)

        return repos 

    def show(self,request,id):
        query = self.db_api.get_repo(id)
        if query is None:
	    return {}
        repo={'id':query.id,
              'repo_path':query.repo_path,
              'project_id':query.project_id,
              'created':isotime(query.created)}

	return repo

    def create(self,request,body):
        project_id=body.get('project_id')
        repo_path=body.get('repo_path')

	try:
            self.db_api.add_repo(dict(
		id = uuid.uuid4().hex,
                repo_path= repo_path,
                project_id = project_id))
        except IntegrityError,err:
	    LOG.error(err)
	    return {"status":500}

        return {"status":200}

    def delete(self,request,id):
        self.db_api.delete_repo(id)

        return {"status":200}

def create_resource():
    return wsgi.Resource(Controller())

