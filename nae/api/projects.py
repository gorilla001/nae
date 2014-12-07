import uuid
from sqlalchemy.exc import IntegrityError
from nae import wsgi
from nae import db
from nae.common.timeutils import isotime
from nae.common import log as logging

LOG = logging.getLogger(__name__)

class Controller(object):
    def __init__(self):
        self.db_api=db.API()

    def index(self,request):
        projects=[]
        user_id = request.GET.get('user_id')
        query = self.db_api.get_projects(user_id=user_id)
        for item in query:
            project={
                'id':item.id,
                'name':item.name,
                'desc':item.desc,
                'created':isotime(item.created),
             }
            projects.append(project)
        return projects 

    def show(self,request,id):
        query = self.db_api.get_project(id)
	if query is None:
            return {}
        project = {"id": query.id,
                   "name": query.name,
                   "desc": query.desc,
                   "created": isotime(query.created)}

        query=self.db_api.get_repos(project_id=id)
        repos=[]
        for item in query:
	    repo = {"id":item.id,
                    "repo_path":item.repo_path,
                    "created":isotime(item.created)}
            repos.append(repo)
        project.update({"repos":repos})

	
        query = self.db_api.get_images(project_id=id)
        images=[]
        for item in query:
            image = {'id' : item.id,
                     'name' : item.name,
		     'tag' : item.tag,
                     'size' : item.size,
                     'desc' : item.desc,
                     'created' : isotime(item.created),
                     'status' : item.status}
            images.append(image)
	project.update({"images":images})

        query = self.db_api.get_containers(id,None)
        containers=[]
        for item in query:
            container = {
                'id':item.id,
                'name':item.name,
                'env':item.env,
                'repos':item.repos,
                'branch':item.branch,
                'image':item.image,
                'network':item.network,
                'created':isotime(item.created),
                'user_id':item.user_id,
                'status':item.status}
        project.update({"containers":containers})

        query = self.db_api.get_users(project_id=id)
	users=[]
        for item in query:
            user={
                'id':item.id,
                'name':item.name,
                'email':item.email,
                'role_id':item.role_id,
                'created':isotime(item.created),
                }
            users.append(user)
	project.update({"users":users})

        return project 

    def create(self,request,body):
        name=body.get('name')
        desc=body.get('desc')

        self.db_api.add_project(dict(
			id = uuid.uuid4().hex,
                        name = name,
                        desc = desc))

        return {"status":200}
        """
        self.db_api.add_user(
            user_id = project_admin,
            user_name = '',
            user_email = admin_email,
            project_id = project_id,
            role_id = 1, # 0 for admin
            created = created_time,
        )
        """ 

    def delete(self,request,id):
        try:
            self.db_api.delete_project(id)
        except IntegrityError,err:
	    LOG.error(err)
	    return {"status":500}

        return {"status":200}

    def update(self,request):
        project_id=request.environ['wsgiorg.routing_args'][1]['id']
        project_name = request.GET['name']
        project_desc = request.GET['desc']
        project_members = request.GET['members']
        project_hgs = request.GET['hgs']
        self.db_api.update_project(
                project_id = project_id,
                project_name = project_name,
                project_desc = project_desc,
                project_members = '',
                project_hgs = '',
                )
        members_list = str(project_members).split()
        self.db_api.delete_users(project_id)
        for member in members_list:
            self.db_api.add_user(
                    project_id = project_id,
                    user_id = member,
                    user_name = '',
                    created = utils.human_readable_time(time.time()),

                )
        repo_list = str(project_hgs).split()
        self.db_api.delete_repos(project_id)
        for hg in hg_list:
            self.db_api.add_repo(
                    project_id = project_id,
                    repo_name = repo,
                    image_id = ''
                    )

        return {"status":"200"}

def create_resource():
    return wsgi.Resource(Controller()) 
