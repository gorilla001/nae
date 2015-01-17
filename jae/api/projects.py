import uuid
import copy
import webob.exc
from sqlalchemy.exc import IntegrityError
from jsonschema import validate

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
        """show project details for `id`"""
        project_instance = self.db.get_project(id)
	if project_instance is None:
            return {}

        """get project user list."""
	user_list = [] 
	for user_instance in project_instance.users:
            user = { "id": user_instance.id, 
                     "name": user_instance.name,
                     "email": user_instance.email,
                     "role_id": user_instance.role_id,
                     "created" : isotime(user_instance.created)} 
            user_list.append(user)

        """"get project repo list."""
 	repo_list =[]
	for repo_instance in project_instance.repos:
	    repo = { "id":repo_instance.id,
		     "repo_path": repo_instance.repo_path,
                     "created": isotime(repo_instance.created)}
            repo_list.append(repo)

        """"get project image list."""
        image_list = []
        for image_instance in project_instance.images:
            image={'id':image_instance.id,
                   'uuid':image_instance.uuid,
                   'name':image_instance.name,
		   'tag':image_instance.tag,
                   'desc':image_instance.desc,
                   'project_id':image_instance.project_id,
                   'created':isotime(image_instance.created),
                   'user_id':image_instance.user_id,
                   'status' : image_instance.status}
            image_list.append(image)

        project = {"id": project_instance.id,
                   "name": project_instance.name,
                   "desc": project_instance.desc,
                   "created": isotime(project_instance.created),
		   "users" : user_list,
                   "repos" : repo_list,
                   "images": image_list}
        
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
        #name=body.get('name')
        #if not name:
	#    LOG.error("project name must be provided")
        #    return Response(505)

        #desc=body.get('desc','')
        schema = { 
            "type": "object",
            "properties": {
                 "name": {"type": "string","minLength":1,"maxLength":255},
                 "desc": {"type": "string"},
             }
        }
        try:
            validate(body,schema)
        except:
            raise

        name = body.pop("name")
        desc = body.pop("desc")

        """generate project id."""
        project_id = uuid.uuid4().hex

        try:
            self.db.add_project(dict(
			id = project_id,
                        name = name,
                        desc = desc))
        except:
            raise

        #FIXME: return ?
        return webob.exc.HTTPOk() 

    def delete(self,request,id):
        """delete project by `id`"""
        LOG.info("DELETE +job delete %s" % id)
        try:
            self.db.delete_project(id)
        except IntegrityError,err:
	    LOG.error(err)
            LOG.info("DELETE -job delete = ERR")
	    return Response(500) 

        LOG.info("DELETE -job delete = OK")
        """return webob.exc.HTTPNoContent() seems more better."""
        return webob.exc.HTTPNoContent()

     

def create_resource():
    return wsgi.Resource(Controller()) 
