import uuid
import copy
from sqlalchemy.exc import IntegrityError
from jae import wsgi
from jae import base
from jae.common.timeutils import isotime
from jae.common import log as logging
from jae.common.response import Response, ResponseObject

LOG = logging.getLogger(__name__)

class Controller(base.Base):
    def __init__(self):
	super(Controller,self).__init__()

    def index(self,request):
        projects=[]
        project_instances = self.db.get_projects()
	if project_instances:
	    for instance in project_instances:
                project={
                        'id':instance.id,
                        'name':instance.name,
                        'desc':instance.desc,
                        'created':isotime(instance.created)}
                projects.append(project)

        return ResponseObject(projects) 

    def show(self,request,id):
        project_instance = self.db.get_project(id)
	if project_instance is None:
            return {}
	user_list = [] 
	for user_instance in project_instance.users:
            user = { "id": user_instance.id, 
                     "name": user_instance.name,
                     "email": user_instance.email,
                     "role_id": user_instance.role_id,
                     "created" : isotime(user_instance.created)} 
            user_list.append(user)
 	repo_list =[]
	for repo_instance in project_instance.repos:
	    repo = { "id":repo_instance.id,
		     "repo_path": repo_instance.repo_path,
                     "created": isotime(repo_instance.created)}
            repo_list.append(repo)

        project = {"id": project_instance.id,
                   "name": project_instance.name,
                   "desc": project_instance.desc,
                   "created": isotime(project_instance.created),
		   "users" : user_list,
                   "repos" : repo_list}

        #query=self.db_api.get_repos(project_id=id)
        #repos=[]
        #for item in query:
	#    repo = {"id":item.id,
        #            "repo_path":item.repo_path,
        #            "created":isotime(item.created)}
        #    repos.append(repo)
        #project.update({"repos":repos})

	#
        #query = self.db_api.get_images(project_id=id)
        #images=[]
        #for item in query:
        #    image = {'id' : item.id,
        #             'name' : item.name,
	#	     'tag' : item.tag,
        #             'size' : item.size,
        #             'desc' : item.desc,
        #             'created' : isotime(item.created),
        #             'status' : item.status}
        #    images.append(image)
	#project.update({"images":images})

        #query = self.db_api.get_containers(id,None)
        #containers=[]
        #for item in query:
        #    container = {
        #        'id':item.id,
        #        'name':item.name,
        #        'env':item.env,
        #        'repos':item.repos,
        #        'branch':item.branch,
        #        'image':item.image,
        #        'network':item.network,
        #        'created':isotime(item.created),
        #        'user_id':item.user_id,
        #        'status':item.status}
        #project.update({"containers":containers})

        #query = self.db_api.get_users(project_id=id)
	#users=[]
        #for item in query:
        #    user={
        #        'id':item.id,
        #        'name':item.name,
        #        'email':item.email,
        #        'role_id':item.role_id,
        #        'created':isotime(item.created),
        #        }
        #    users.append(user)
	#project.update({"users":users})

        return ResponseObject(project) 

    def create(self,request,body):
        """add project."""
        name=body.get('name')
        desc=body.get('desc')
        project_id = uuid.uuid4().hex
        self.db.add_project(dict(
			id = project_id,
                        name = name,
                        desc = desc))
        """add admin."""
	admin = body.get('admin')
	email = body.get('email')
        project = self.db.get_project(project_id)
        self.db.add_user(dict(
		id = uuid.uuid4().hex,
                name = admin,
                email = email,
                role_id = 0),
                project = copy.deepcopy(project))

        """add base image."""
        #self.db.add_image(dict(
	#	id=id,
	#	uuid = uuid,
	#	name=name,
	#	tag=tag,
	#	desc

        return Response(201) 
        """
                """ 

    def delete(self,request,id):
        try:
            self.db.delete_project(id)
        except IntegrityError,err:
	    LOG.error(err)
	    return Response(500) 

        return Response(201) 

    def update(self,request):
        project_id=request.environ['wsgiorg.routing_args'][1]['id']
        project_name = request.GET['name']
        project_desc = request.GET['desc']
        project_members = request.GET['members']
        project_hgs = request.GET['hgs']
        self.db.update_project(
                project_id = project_id,
                project_name = project_name,
                project_desc = project_desc,
                project_members = '',
                project_hgs = '',
                )
        members_list = str(project_members).split()
        self.db.delete_users(project_id)
        for member in members_list:
            self.db.add_user(
                    project_id = project_id,
                    user_id = member,
                    user_name = '',
                    created = utils.human_readable_time(time.time()),

                )
        repo_list = str(project_hgs).split()
        self.db.delete_repos(project_id)
        for hg in hg_list:
            self.db.add_repo(
                    project_id = project_id,
                    repo_name = repo,
                    image_id = ''
                    )

        return {"status":"200"}

def create_resource():
    return wsgi.Resource(Controller()) 
